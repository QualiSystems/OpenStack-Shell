from cloudshell.cp.openstack.common.deploy_data_holder import DeployDataHolder

from cloudshell.cp.openstack.models.connectivity_action_result_model import ConnectivityActionResultModel
from cloudshell.cp.openstack.models.driver_response_model import DriverResponse, DriverResponseRoot
from cloudshell.cp.openstack.models.connectivity_action_resource_info import ConnectivityActionResourceInfo
import jsonpickle

from cloudshell.cp.openstack.domain.services.nova.nova_instance_service import NovaInstanceService
from cloudshell.cp.openstack.domain.services.waiters.instance import InstanceWaiter
from cloudshell.cp.openstack.domain.services.neutron.neutron_network_service import NeutronNetworkService
from threading import Lock
import traceback


class VLANConnectivityService(object):
    """
    Class implementing Business Logic for VLAN Connectivity.
    """
    def __init__(self, instance_service, network_service):
        """

        :param NovaInstanceService instance_service:
        :param NeutronNetworkService network_service:
        """
        self.network_service = network_service
        self.instance_service = instance_service
        self.subnet_lock = Lock()

    def perform_apply_connectivity(self, openstack_session, cp_resource_model, connection_request, logger):
        """

        :param keystoneauth1.session.Session openstack_session:
        :param OpenStackResourceModel cp_resource_model:
        :param str connection_request:
        :param LoggingSessionContext logger:
        :return:
        """

        conn_req_deploy_data = DeployDataHolder(jsonpickle.decode(connection_request))

        # Now collect following dict
        # Key: (vlanID)
        # value: List of (Resource_Name, VM_UUID, actionID)
        # For each item, create network, and assign a nic on that network

        actions = conn_req_deploy_data.driverRequest.actions

        set_vlan_actions_dict = {}
        remove_vlan_actions_dict = {}

        # Add more description
        # TODO : implement remove actions dict
        for action in actions:

            curr_dict = self._get_curr_actions_dict(action_type=action.type,
                                                    set_vlan_action_dict=set_vlan_actions_dict,
                                                    remove_vlan_action_dict=remove_vlan_actions_dict)
            if curr_dict is None:
                raise ValueError("Unknown action: Action not one of 'setVlan' or 'removeVlan'.")

            actionid = action.actionId
            deployed_app_res_name = action.actionTarget.fullName
            action_resource_info = self.get_action_resource_info(deployed_app_res_name, actionid, action)

            action_vlanid = action.connectionParams.vlanId
            if action_vlanid in curr_dict.keys():
                curr_dict[action_vlanid].append(action_resource_info)
            else:
                curr_dict[action_vlanid] = [action_resource_info]

        results = []
        if set_vlan_actions_dict:
            result = self.set_vlan_actions(openstack_session=openstack_session,
                                           cp_resource_model=cp_resource_model,
                                           vlan_actions=set_vlan_actions_dict,
                                           logger=logger)
            results += result

        if remove_vlan_actions_dict:
            result = self.remove_vlan_actions(openstack_session=openstack_session,
                                              cp_resource_model=cp_resource_model,
                                              vlan_actions=remove_vlan_actions_dict,
                                              logger=logger)
            results += result

        # We have apply Connectivity results - We should send out the JSON and encode it
        driver_response = DriverResponse()
        driver_response.actionResults = results
        driver_response_root = DriverResponseRoot()
        driver_response_root.driverResponse = driver_response

        return driver_response_root

    def _format_err_msg_for_exception(self, e):
        """
        :param Exception e:
        :return:
        """
        err_msg = e.message
        err_msg = err_msg.replace("<", "(").replace(">", ")")
        return err_msg

    def set_vlan_actions(self, openstack_session, cp_resource_model, vlan_actions, logger):
        """

        :param keystoneauth1.session.Session openstack_session:
        :param OpenStackResourceModel cp_resource_model:
        :param dict vlan_actions:
        :param LoggingSessionContext logger:
        :return ConnectivityActionResult List :
        """

        # For each VLAN ID (create VLAN network)
        results = []

        for vlan_id, values in vlan_actions.iteritems():
            net = None
            net_err_msg = ''
            try:
                net = self.network_service.create_or_get_network_with_segmentation_id(
                    openstack_session=openstack_session,
                    cp_resource_model=cp_resource_model,
                    segmentation_id=int(vlan_id),
                    logger=logger)
            except Exception as e:
                logger.error(traceback.format_exc())
                net_err_msg = self._format_err_msg_for_exception(e)
            if not net:
                fail_results = self.set_fail_results(values=values,
                                                     action_type='setVlan',
                                                     failure_text="Failed to Create Network with VLAN ID {0}. "
                                                                  "Error: {1}".format(vlan_id, net_err_msg))
                results += fail_results
            else:
                subnet = None
                subnet_err_msg = ''
                try:
                    net_id = net['id']
                    subnet = net['subnets']
                    if not subnet:
                        with self.subnet_lock:
                            subnet = self.network_service.create_and_attach_subnet_to_net(
                                openstack_session=openstack_session,
                                cp_resource_model=cp_resource_model,
                                net_id=net_id,
                                logger=logger)
                            subnet_err_msg = 'empty_subnet'
                    else:
                        subnet = subnet[0]
                except Exception as e:
                    logger.error(traceback.format_exc())
                    subnet_err_msg = self._format_err_msg_for_exception(e)
                if not subnet:
                    fail_results = self.set_fail_results(values=values,
                                                         action_type='setVlan',
                                                         failure_text="Failed to attach Subnet to Network {0}. "
                                                                      "Error: {1}".format(net_id, subnet_err_msg))
                    results += fail_results
                else:
                    attach_results = []
                    for val in values:
                        action_result = self.attach_nic_to_instance_action_result(openstack_session=openstack_session,
                                                                                  action_resource_info=val,
                                                                                  net_id=net_id,
                                                                                  logger=logger)
                        attach_results.append(action_result)
                    results += attach_results
        return results

    def remove_vlan_actions(self, openstack_session, cp_resource_model, vlan_actions, logger):
        """
        Function implementing Remove VLANs in apply_connectivity
        :param keystoneauth1.session.Session openstack_session:
        :param OpenStckResourceModel cp_resource_model:
        :param dict vlan_actions:
        :param LoggingSessionContext logger:
        :return:
        """

        results = []

        for k, values in vlan_actions.iteritems():
            net = self.network_service.get_network_with_segmentation_id(openstack_session=openstack_session,
                                                                        segmentation_id=int(k), logger=logger)
            if not net:
                fail_results = self.set_fail_results(values=values,
                                                     action_type='removeVlan',
                                                     failure_text="Failed to get Network with VLAN ID {0}".format(k))
                results += fail_results
            else:
                net_id = net['id']

                remove_results = []
                for val in values:
                    action_result = self.detach_nic_from_instance_action_result(openstack_session=openstack_session,
                                                                                action_resource_info=val,
                                                                                net_id=net_id,
                                                                                logger=logger)
                    remove_results.append(action_result)

                results += remove_results

                # We should just remove subnet(s) and net from Openstack now (If any exception that gets logged)
                with self.subnet_lock:
                    self.network_service.remove_subnet_and_net(openstack_session=openstack_session,
                                                               network=net, logger=logger)

        return results

    def set_fail_results(self, values, failure_text, action_type, logger=None):
        """
        For all connections (obtained from values), set the failed results text, useful in generating output
        :param tuple values:
        :param str failure_text:
        :param str action_type:
        :param logger:
        :return ConnectivityActionResultModel List:
        """
        results = []
        for value in values:
            action_result = ConnectivityActionResultModel()
            action_result.success = False
            action_result.actionId = value.actionid
            action_result.infoMessage = None
            action_result.errorMessage = failure_text
            action_result.type = action_type
            action_result.updatedInterface = None
            results.append(action_result)
        return results

    def _get_curr_actions_dict(self, action_type, set_vlan_action_dict=None, remove_vlan_action_dict=None):
        """

        :param str action_type:
        :param dict set_vlan_action_dict:
        :param dict remove_vlan_action_dict:
        :return:
        """
        if action_type == 'setVlan' and set_vlan_action_dict is not None:
            return set_vlan_action_dict

        elif action_type == 'removeVlan' and remove_vlan_action_dict is not None:
            return remove_vlan_action_dict

        return None

    def get_action_resource_info(self, deployed_app_resource_name, actionid, action):
        """

        :param str deployed_app_resource_name:
        :param str actionid:
        :param action: action obtained from JSON
        :return ConnectivityActionResourceInfo:

        """

        custom_action_attributes = action.customActionAttributes
        vm_uuid = None

        for cust_attr in custom_action_attributes:
            if cust_attr.attributeName == 'VM_UUID':
                vm_uuid = cust_attr.attributeValue

        connector_attributes = action.connectorAttributes

        # in removeVlan
        iface_ip = None
        iface_port_id = None
        iface_mac = None
        if connector_attributes:
            for conn_attribute in connector_attributes:
                if conn_attribute.attributeName == 'Interface':
                    attr_dict = jsonpickle.loads(conn_attribute.attributeValue)
                    iface_ip = attr_dict['ip_address']
                    iface_port_id = attr_dict['port_id']
                    iface_mac = attr_dict['mac_address']

        return ConnectivityActionResourceInfo(deployed_app_resource_name=deployed_app_resource_name,
                                              actionid=actionid,
                                              vm_uuid=vm_uuid,
                                              interface_ip=iface_ip,
                                              interface_port_id=iface_port_id,
                                              interface_mac=iface_mac)

    def attach_nic_to_instance_action_result(self, openstack_session, action_resource_info, net_id, logger):
        """

        :param keystoneauth1.session.Session openstack_session:
        :param ConnectivityActionResourceInfo action_resource_info:
        :param str net_id:
        :param LoggingSessionContext logger:
        :return ConnectivityActionResultModel:
        """
        action_result = ConnectivityActionResultModel()

        result = None
        result_err_msg = ''
        try:
            instance_id = action_resource_info.vm_uuid
            result = self.instance_service.attach_nic_to_net(openstack_session=openstack_session,
                                                             instance_id=instance_id, net_id=net_id, logger=logger)
        except Exception as e:
            result_err_msg = self._format_err_msg_for_exception(e)
            logger.error(result_err_msg)
        if not result:
            action_result.success = "False"
            action_result.actionId = action_resource_info.actionid
            action_result.errorMessage = "Failed to Attach NIC on Network {0} to Instance {1}." \
                                         "Raised Exception: {2} ".format(net_id,
                                                                         action_resource_info.deployed_app_resource_name,
                                                                         result_err_msg)
            action_result.infoMessage = ""
            action_result.updatedInterface = ""
            action_result.type = 'setVlan'
        else:
            action_result.success = "True"
            action_result.actionId = action_resource_info.actionid
            action_result.errorMessage = ""
            action_result.infoMessage = "Successfully Attached NIC on Network {0} to Instance {1}".format(
                    net_id,
                    action_resource_info.deployed_app_resource_name)
            action_result.updatedInterface = result
            action_result.type = 'setVlan'

        return action_result

    def detach_nic_from_instance_action_result(self, openstack_session, action_resource_info, net_id, logger):
        """

        :param keystoneauth1.session.Session openstack_session:
        :param ConnectivityActionResourceInfo action_resource_info:
        :param str net_id:
        :param LoggingSessionContext logger:
        :return ConnectivityActionResultModel:
        """
        action_result = ConnectivityActionResultModel()

        port_id = action_resource_info.interface_port_id
        vm_uuid = action_resource_info.vm_uuid
        result_err_msg = ''
        result = None
        try:

            result = self.instance_service.detach_nic_from_instance(openstack_session=openstack_session,
                                                                    instance_id=vm_uuid, port_id=port_id, logger=logger)
        except Exception as e:
            result_err_msg = self._format_err_msg_for_exception(e)
            logger.error(result_err_msg)
        if not result:
            action_result.success = "False"
            action_result.actionId = action_resource_info.actionid
            action_result.errorMessage = "Failed to Detach NIC {0} from Instance {1}. Error {2}".format(
                    port_id,
                    action_resource_info.deployed_app_resource_name,
                    result_err_msg)
            action_result.infoMessage = ""
            action_result.updatedInterface = ""
            action_result.type = 'removeVlan'
        else:
            action_result.success = "True"
            action_result.actionId = action_resource_info.actionid
            action_result.errorMessage = ""
            action_result.infoMessage = "Successfully detached NIC {0} from Instance {1}".format(
                    port_id,
                    action_resource_info.deployed_app_resource_name)
            action_result.updatedInterface = result
            action_result.type = 'removeVlan'

        return action_result
