"""
Implements a concrete DeployOperation class.
"""

# Domain Services
from cloudshell.cp.openstack.domain.services.nova.nova_instance_service import NovaInstanceService
from cloudshell.cp.openstack.domain.services.waiters.instance import InstanceWaiter

# Results
from cloudshell.cp.openstack.models.deploy_result_model import DeployResultModel

class DeployOperation(object):
    def __init__(self):
        self.instance_waiter = InstanceWaiter()
        self.instance_service = NovaInstanceService(self.instance_waiter)

    def deploy(self, os_session, name, reservation, cp_resource_model, deploy_req_model, logger):
        """
        Performs actual deploy operation.
        :param keystoneauth1.session.Session os_session:
        :param str name: Name of the instance to be deployed
        :param ReservationModel reservation:
        :param DeployDataHolder deploy_req_model:
        :param OpenStackResourceModel cp_resource_model:
        :param LoggingSessionContext logger:
        :rtype DeployResultModel:
        """
        logger.info("Inside Deploy Operation.")
        # First create instance
        instance = self.instance_service.create_instance(openstack_session=os_session,
                                                         name=name,
                                                         reservation=reservation,
                                                         cp_resource_model=cp_resource_model,
                                                         deploy_req_model=deploy_req_model,
                                                         logger=logger)

        # Actually cannot come here and instance is None. If the previous statement raised an Exception let it go
        # uncaught - so this goes all the way to the UI.
        if instance is None:
            return None

        logger.info("Deploy Operation Done. Instance Created: {0}:{1}".format(
            instance.name,
            instance.id
        ))

        # Get Private Network
        private_network_name = self.instance_service.get_instance_mgmt_network_name(instance=instance,
                                                                                    openstack_session=os_session,
                                                                                    cp_resource_model=cp_resource_model)
        if private_network_name is None:
            raise ValueError("Management network with ID for instance not found". \
                             format(cp_resource_model.qs_mgmt_os_net_id))

        # Assign floating IP
        floating_ip = ''
        if deploy_req_model.add_floating_ip:
            if deploy_req_model.external_network_uuid:
                floating_ip_net_uuid = deploy_req_model.external_network_uuid
            else:
                floating_ip_net_uuid = cp_resource_model.external_network_uuid

            floating_ip = self.instance_service.assign_floating_ip(instance=instance,
                                                                   openstack_session=os_session,
                                                                   cp_resource_model=cp_resource_model,
                                                                   floating_ip_net_uuid=floating_ip_net_uuid,
                                                                   logger=logger)
        # Get private IP
        private_ip_address = self.instance_service.get_private_ip(instance, private_network_name)

        deployed_app_attributes = dict()
        deployed_app_attributes['Public IP'] = floating_ip

        return DeployResultModel(vm_name=instance.name,
                                 vm_uuid=instance.id,
                                 cloud_provider_name=deploy_req_model.cloud_provider,
                                 deployed_app_ip=private_ip_address,
                                 deployed_app_attributes=deployed_app_attributes,
                                 floating_ip=floating_ip)