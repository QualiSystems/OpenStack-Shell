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

    def deploy(self, os_session, name, reservation, deploy_req_model, logger):
        """
        Performs actual deploy operation.
        :param os_session:
        :type os_session:
        :param name: Name of the instance to be deployed
        :type name: str
        :param reservation:
        :type reservation: str
        :param deploy_req_model:
        :type deploy_req_model:
        :param logger:
        :type logger:
        :return :
        :rtype DeployResultModel
        """
        logger.info("Inside Deploy Operation.")
        # First create instance
        instance = self.instance_service.create_instance(openstack_session=os_session,
                                                         name=name,
                                                         reservation=reservation,
                                                         deploy_req_model=deploy_req_model,
                                                         logger=logger)

        # Get security groups For inbound/outbound ports
        # sgs = self.instance_service.get_security_groups(os_session,
        #                                instance)

        # Get Private IP
        if instance == None:
            return None, "Error in creating instance"
        # Populate all instance data
        logger.info("Deploy Operation Done. Instance Created: {0}:{1}".format(
            instance.name,
            instance.id
        ))

        # FIXME: generate DeployResultModel and return
        return DeployResultModel(vm_name=instance.name,
                                 vm_uuid=instance.id,
                                 cloud_provider_name=deploy_req_model.cloud_provider), None
