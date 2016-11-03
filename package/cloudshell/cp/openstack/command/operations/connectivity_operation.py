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
            # FIXME: Move this "ifs into a separate function
            if action.type == 'setVlan':
                curr_dict = set_vlan_actions_dict
            # FIXME: Check whether this is 'removeVlan'
            else:
                curr_dict = remove_vlan_actions_dict

            action_vlanid = action.connectionParams.vlanId
            actionid = action.actionId

            deployed_app_res_name = action.actionTarget.fullName

            for cust_attr in action.customActionAttributes :
                if cust_attr.attributeName == 'VM_UUID':
                    vm_uuid = cust_attr.attributeValue
                    # FIXME : changed this to object for later readability
                    resource_info = (deployed_app_res_name, vm_uuid, actionid)
            if action_vlanid in curr_dict.keys():
                curr_dict[action_vlanid].append(resource_info)
            else:
                curr_dict[action_vlanid] = [resource_info]

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
                                                  vlan_actions=set_vlan_actions_dict,
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
            # FIXME: results getting overwritten
            # FIXME: update the nethod name
            net = self.network_service.create_network_with_vlanid(openstack_session=openstack_session,
                                                                  vlanid=int(k),
                                                                  logger=logger)
            if not net:
                # FIXME : create error for the action
                results = self._set_fail_results(values=values,
                                                 action_type='setVlan',
                                                 failure_text="Failed to Create Network with VLAN ID {0}".format(k))
            else:
                net_id = net['id']

                subnet = net['subnets']
                if not subnet:
                    # FIXME: Rename this function to create_and_attach
                    subnet = self.network_service.attach_subnet_to_net(openstack_session=openstack_session,
                                                                       cp_resource_model=cp_resource_model,
                                                                       net_id=net_id,
                                                                       logger=logger)
                else:
                    subnet = subnet[0]
                if not subnet:
                    # FIXME: create error for action
                    results = self._set_fail_results(values=values,
                                                     action_type='setVlan',
                                                     failure_text="Failed to attach Subnet to Network {0}".format(net_id))
                else:
                    attach_results = []
                    # FIXME: let's move this
                    for val in values:

                        instance_id = val[1]
                        # returns MAC Address of the attached port - which is reflected in updated Port
                        result = self.instance_service.attach_nic_to_net(openstack_session, instance_id, net_id, logger)
                        if not result:
                            action_result = ConnectivityActionResultModel()
                            action_result.success = False
                            action_result.actionId = val[2]
                            action_result.errorMessage = \
                                "Failed to Attach NIC on Network {0} to Instance {1}".format(net_id, val[0])
                            action_result.infoMessage = None
                            action_result.updatedInterface = None
                        else:
                            action_result = ConnectivityActionResultModel()
                            action_result.success = "True"
                            action_result.actionId = val[2]
                            action_result.errorMessage = ""
                            action_result.infoMessage = \
                                "Successfully Attached NIC on Network {0} to Instance {1}".format(net_id, val[0])
                            action_result.updatedInterface = result
                            action_result.type = 'setVlan'
                        attach_results.append(action_result)
                    results = attach_results
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
        logger.info("_do_remove_vlan_actions called.")
        return []

    def _set_fail_results(self, values, failure_text, action_type, logger=None):
        """
        For all connections (obtained from values), set the failed results text, useful in generating output
        :param tuple values:
        :param str failure_text:
        :param str action_type
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