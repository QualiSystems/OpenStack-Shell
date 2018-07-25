"""
Implements a concrete DeployOperation class.
"""

# Domain Services
from cloudshell.cp.openstack.domain.common.vm_details_provider import VmDetailsProvider
from cloudshell.cp.openstack.domain.services.nova.nova_instance_service import NovaInstanceService
import traceback
from cloudshell.cp.core.models import DeployAppResult,Attribute

class DeployOperation(object):
    def __init__(self, instance_service, network_service, cancellation_service, vm_details_provider):
        """

        :param NovaInstanceService instance_service:
        :param NeutronNetworkService network_service:
        :param cancellation_service:
        :param cloudshell.cp.openstack.domain.common.vm_details_provider.VmDetailsProvider vm_details_provider:
        """
        self.cancellation_service = cancellation_service
        self.instance_service = instance_service
        self.network_service = network_service
        self.vm_details_provider = vm_details_provider

    def deploy(self, os_session, reservation, cp_resource_model, deploy_app_action, cancellation_context, logger):
        """
        Performs actual deploy operation.
        :param keystoneauth1.session.Session os_session:
        :param ReservationModel reservation:
        :param cloudshell.cp.core.models.DeployApp deploy_app_action:
        :param OpenStackResourceModel cp_resource_model:
        :param cloudshell.shell.core.context.CancellationContext cancellation_context:
        :param logging.Logger logger:
        :rtype DeployResultModel:
        """
        logger.info("Inside Deploy Operation.")
        # First create instance
        instance = None
        floating_ip_str = ''
        action_id = deploy_app_action.actionId

        try:
            # Check for cancellation right at the beginning
            self.cancellation_service.check_if_cancelled(cancellation_context=cancellation_context)
            deploy_req_model = deploy_app_action.actionParams.deployment.customModel
            instance = self.instance_service.create_instance(openstack_session=os_session,
                                                             name=deploy_app_action.actionParams.appName,
                                                             reservation=reservation,
                                                             cp_resource_model=cp_resource_model,
                                                             deploy_req_model=deploy_app_action.actionParams.deployment.customModel,
                                                             cancellation_context=cancellation_context,
                                                             logger=logger)

            # Actually cannot come here and instance is None. If the previous statement raised an Exception,
            # we'd deal with it in the except cause.
            if instance is None:
                return DeployAppResult(actionId=action_id, success=False, errorMessage='Create Instance Returned None')

            logger.info("Deploy Operation Done. Instance Created: {0}:{1}".format(instance.name, instance.id))

            # Get Private Network
            private_network_name = self.instance_service.get_instance_mgmt_network_name(instance=instance,
                                                                                        openstack_session=os_session,                                                                                        cp_resource_model=cp_resource_model)
            # if private_network_name is None:
            #     return DeployAppResult(actionId=action_id, success=False,
            #                            errorMessage="Management network with ID '{}' for instance not found".format(
            #                                cp_resource_model.qs_mgmt_os_net_id))

            if private_network_name is None:
                raise ValueError("Management network with ID '{}' for instance not found".format(cp_resource_model.qs_mgmt_os_net_id))

            # Assign floating IP
            if deploy_req_model.add_floating_ip:
                floating_ip_subnet_uuid = deploy_req_model.floating_ip_subnet_id if deploy_req_model.floating_ip_subnet_id else cp_resource_model.floating_ip_subnet_uuid

                floating_ip_dict = self.network_service.create_floating_ip(
                    floating_ip_subnet_id=floating_ip_subnet_uuid,
                    openstack_session=os_session,
                    logger=logger)
                if floating_ip_dict:
                    floating_ip_str = floating_ip_dict['floating_ip_address']
                if floating_ip_str:
                    self.instance_service.attach_floating_ip(instance=instance,
                                                             floating_ip=floating_ip_str,
                                                             openstack_session=os_session,
                                                             logger=logger)
                else:
                    raise ValueError("Unable to assign Floating IP on Subnet {}".format(floating_ip_subnet_uuid))


            # Get private IP
            private_ip_address = self.instance_service.get_private_ip(instance, private_network_name)

            # Just make sure we were not cancelled before returning result.
            self.cancellation_service.check_if_cancelled(cancellation_context=cancellation_context)

            management_vlan_id = cp_resource_model.qs_mgmt_os_net_uuid

            logger.info("management_vlan_id is: {0}.".format(management_vlan_id))

            vm_details_data = self.vm_details_provider.create(instance=instance, openstack_session=os_session,
                                                              management_vlan_id=management_vlan_id,
                                                              logger=logger)
            public_ip_attr = Attribute('Public IP',floating_ip_str)
            deployed_app_attributes = [public_ip_attr]

            return DeployAppResult(actionId=action_id, success=True,vmUuid=instance.id,vmName=instance.name,deployedAppAddress=private_ip_address,deployedAppAttributes=deployed_app_attributes, vmDetailsData=vm_details_data)

        # If any Exception is raised during deploy or assign floating IP - clean up OpenStack side and re-raise
        except Exception as e:
            logger.error(traceback.format_exc())

            self._rollback_failed_instance(logger=logger,
                                           os_session=os_session,
                                           floating_ip=floating_ip_str,
                                           instance=instance)

            # Re-raise for the UI
            return DeployAppResult(actionId=action_id, success=False,
                                   errorMessage=e.message)


    def _rollback_failed_instance(self, logger, os_session, floating_ip, instance):
        """

        :param logging.Logger logger:
        :param keystoneauth1.session.Session os_session:
        :param str floating_ip:
        :param novaclient.Client.servers.Server instance:
        :return:
        """
        if not instance:
            return
        instance_id = instance.id

        # This calls detach and delete floating IP and instance terminate (handles empty floating IP)
        try:
            self.instance_service.detach_floating_ip(openstack_session=os_session,
                                                     instance=instance,
                                                     floating_ip=floating_ip,
                                                     logger=logger)
            self.network_service.delete_floating_ip(openstack_session=os_session,
                                                    floating_ip=floating_ip,
                                                    logger=logger)
        except Exception:
            logger.exception("Failed to remove floating ip {}. ".format(floating_ip))

        self.instance_service.terminate_instance(openstack_session=os_session,
                                                 instance_id=instance_id,
                                                 logger=logger)
