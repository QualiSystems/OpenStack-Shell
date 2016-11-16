from cloudshell.cp.openstack.domain.services.nova.nova_instance_service import NovaInstanceService
from cloudshell.cp.openstack.domain.services.neutron.neutron_network_service import NeutronNetworkService
from cloudshell.cp.openstack.domain.services.waiters.instance import InstanceWaiter

from cloudshell.cp.openstack.common.deploy_data_holder import DeployDataHolder

from cloudshell.cp.openstack.models.connectivity_action_result_model import ConnectivityActionResultModel
from cloudshell.cp.openstack.models.driver_response_model import DriverResponse, DriverResponseRoot

import jsonpickle

class ConnectivityOperation(object):
    public_ip = "Public IP"

    def __init__(self):
        self.instance_waiter = InstanceWaiter()
        self.instance_service = NovaInstanceService(self.instance_waiter)
        self.network_service = NeutronNetworkService()

    def refresh_ip(self, openstack_session, cloudshell_session,
                   deployed_app_resource, private_ip, resource_fullname,
                   logger):
        """

        :param keystoneauth1.session.Session openstack_session:
        :param CloudShellSessionContext cloudshell_session:
        :param deployed_app_resource:
        :param str private_ip:
        :param str resource_fullname:
        :param LoggingSessionContext logger:
        :rtype None:
        """
        logger.info(deployed_app_resource.attributes)
        logger.info(private_ip)
        logger.info("Refresh_IP called")

        instance_id = deployed_app_resource.vmdetails.uid
        instance = self.instance_service.get_instance_from_instance_id(openstack_session=openstack_session,
                                                                       instance_id=instance_id,
                                                                       logger=logger)
        if instance is None:
            raise ValueError("Instance with InstanceID {0} not found".format(instance_id))

        new_private_ip = self.instance_service.get_private_ip(instance)
        if new_private_ip != private_ip:
            cloudshell_session.UpdateResourceAddress(resource_fullname, new_private_ip)

        # FIXME : hardcoded public IP right now. Get it from floating IP later.
        cloudshell_session.SetAttributeValue(resource_fullname, ConnectivityOperation.public_ip, "192.168.1.1")

    def apply_connectivity(self, openstack_session, cp_resource_model, conn_request, logger):
        """
        Implements Apply connectivity - parses the conn_requests and creates
        :param keystoneauth1.session.Session openstack_session:
        :param OpenStackResourceModel cp_resource_model:
        :param str conn_request: Connectivty Request JSON
        :return DriverResponseRoot:
        """

        conn_req_deploy_data = DeployDataHolder(jsonpickle.decode(conn_request))

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
            action_resource_info = self._get_action_resource_info(deployed_app_res_name, actionid, action)

            action_vlanid = action.connectionParams.vlanId
            if action_vlanid in curr_dict.keys():
                curr_dict[action_vlanid].append(action_resource_info)
            else:
                curr_dict[action_vlanid] = [action_resource_info]

        results = []
        if set_vlan_actions_dict:
            result = self._do_set_vlan_actions(openstack_session=openstack_session,
                                               cp_resource_model=cp_resource_model,
                                               vlan_actions=set_vlan_actions_dict,
                                               logger=logger)
            results += result

        if remove_vlan_actions_dict:
            result = self._do_remove_vlan_actions(openstack_session=openstack_session,
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

    def _do_set_vlan_actions(self, openstack_session, cp_resource_model, vlan_actions, logger):
        """

        :param keystoneauth1.session.Session openstack_session:
        :param OpenStackResourceModel cp_resource_model:
        :param dict vlan_actions:
        :param LoggingSessionContext logger:
        :return ConnectivityActionResult List :
        """

        # For each VLAN ID (create VLAN network)
        results = []

        for k, values in vlan_actions.iteritems():
            net = self.network_service.create_or_get_network_with_vlanid(openstack_session=openstack_session,
                                                                  vlanid=int(k),
                                                                  logger=logger)
            if not net:
                fail_results = self._set_fail_results(values=values,
                                                      action_type='setVlan',
                                                      failure_text="Failed to Create Network with VLAN ID {0}".format(k))
                results += fail_results
            else:
                net_id = net['id']

                subnet = net['subnets']
                if not subnet:
                    # FIXME: serialize this
                    # FIXME: Rename this function to create_and_attach
                    subnet = self.network_service.attach_subnet_to_net(openstack_session=openstack_session,
                                                                       cp_resource_model=cp_resource_model,
                                                                       net_id=net_id,
                                                                       logger=logger)
                else:
                    subnet = subnet[0]
                if not subnet:
                    fail_results = self._set_fail_results(values=values,
                                                          action_type='setVlan',
                                                          failure_text="Failed to attach Subnet to Network {0}".format(net_id))
                    results += fail_results
                else:
                    attach_results = []
                    for val in values:
                        action_result = self._attach_nic_to_instance_action_result(openstack_session=openstack_session,
                                                                                   action_resource_info=val,
                                                                                   net_id=net_id,
                                                                                   logger=logger)
                        attach_results.append(action_result)
                    results += attach_results
        return results

    def _do_remove_vlan_actions(self, openstack_session, cp_resource_model, vlan_actions, logger):
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
            net = self.network_service.get_network_with_vlanid(openstack_session=openstack_session,
                                                               vlanid=int(k), logger=logger)
            if not net:
                fail_results = self._set_fail_results(values=values,
                                                      action_type='removeVlan',
                                                      failure_text="Failed to get Network with VLAN ID {0}".format(k))
                results += fail_results
            else:
                net_id = net['id']

                remove_results = []
                for val in values:
                    action_result = self._detach_nic_from_instance_action_result(openstack_session=openstack_session,
                                                                                 action_resource_info=val,
                                                                                 net_id=net_id,
                                                                                 logger=logger)
                    remove_results.append(action_result)
                
                results += remove_results

                # We should just remove subnet(s) and net from Openstack now (If any exception that gets logged)
                # FIXME: Add synchronization here, when moved to a domain service.
                self.network_service.remove_subnet_and_net(openstack_session=openstack_session,
                                                           network=net, logger=logger)

        return results

    def _set_fail_results(self, values, failure_text, action_type, logger=None):
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
            action_result.actionId = value[2]
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

    def _get_action_resource_info(self, deployed_app_resource_name, actionid, action):
        """

        :param str deployed_app_resource_name:
        :param str actionid:
        :param action: action obtained from JSON
        :return ActionResourceInfo:

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
                    iface_ip, iface_port_id, iface_mac = conn_attribute.attributeValue.split("/")

        return ActionResourceInfo(deployed_app_resource_name=deployed_app_resource_name,
                                  actionid=actionid,
                                  vm_uuid=vm_uuid,
                                  interface_ip=iface_ip,
                                  interface_port_id=iface_port_id,
                                  interface_mac=iface_mac)

    def _attach_nic_to_instance_action_result(self, openstack_session, action_resource_info, net_id, logger):
        """

        :param keystoneauth1.session.Session openstack_session:
        :param ActionResourceInfo action_resource_info:
        :param str net_id:
        :param LoggingSessionContext logger:
        :return ConnectivityActionResultModel:
        """
        action_result = ConnectivityActionResultModel()

        instance_id = action_resource_info.vm_uuid
        result = self.instance_service.attach_nic_to_net(openstack_session, instance_id, net_id, logger)
        if not result:
            action_result.success = "False"
            action_result.actionId = action_resource_info.actionid
            action_result.errorMessage = "Failed to Attach NIC on Network {0} to Instance {1}".format(
                                                                        net_id,
                                                                        action_resource_info.deployed_app_resource_name)
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


    def _detach_nic_from_instance_action_result(self, openstack_session, action_resource_info, net_id, logger):
        """

        :param keystoneauth1.session.Session openstack_session:
        :param ActionResourceInfo action_resource_info:
        :param str net_id:
        :param LoggingSessionContext logger:
        :return ConnectivityActionResultModel:
        """
        action_result = ConnectivityActionResultModel()

        port_id = action_resource_info.interface_port_id
        vm_uuid = action_resource_info.vm_uuid

        result = self.instance_service.detach_nic_from_instance(openstack_session=openstack_session,
                                                                instance_id=vm_uuid, port_id=port_id, logger=logger)
        if not result:
            action_result.success = "False"
            action_result.actionId = action_resource_info.actionid
            action_result.errorMessage = "Failed to Detach NIC {0} from Instance {1}".format(
                port_id,
                action_resource_info.deployed_app_resource_name)
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


# FIXME : Move this out to a different place
class ActionResourceInfo:

    def __init__(self, deployed_app_resource_name, actionid, vm_uuid, interface_ip, interface_port_id, interface_mac):
        self.deployed_app_resource_name = deployed_app_resource_name
        self.vm_uuid = vm_uuid
        self.actionid = actionid
        self.iface_ip = interface_ip
        self.interface_port_id = interface_port_id
        self.interface_mac = interface_mac
