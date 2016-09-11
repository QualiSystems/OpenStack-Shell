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
        :param XXX cp_resource_model:
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

        # Get security groups For inbound/outbound ports
        # sgs = self.instance_service.get_security_groups(os_session,
        #                                instance)

        # Actually cannot come here and instance is None. If the previous statement raised an Exception let it go
        # uncaught - so this goes all the way to the UI.
        if instance == None:
            return None

        # Populate all instance data
        # unique name

        logger.info("Deploy Operation Done. Instance Created: {0}:{1}".format(
            instance.name,
            instance.id
        ))

        private_ip_address = self.instance_service.get_private_ip(instance)
        # FIXME: generate DeployResultModel and return
        return DeployResultModel(vm_name=instance.name,
                                 vm_uuid=instance.id,
                                 cloud_provider_name=deploy_req_model.cloud_provider,
                                 deployed_app_ip=private_ip_address)
