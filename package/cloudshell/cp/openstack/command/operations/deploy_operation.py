"""
Implements a concrete DeployOperation class.
"""

# Domain Services
from cloudshell.cp.openstack.domain.services.nova.nova_instance_service \
                                    import NovaInstanceService
from cloudshell.cp.openstack.domain.services.waiters.instance \
                                    import InstanceWaiter

# Results
from cloudshell.cp.openstack.models.deploy_result_model import DeployResultModel

class DeployOperation(object):
    def __init__(self):
        self.instance_waiter = InstanceWaiter()
        self.instance_servie = NovaInstanceService(self.instance_waiter)

    def deploy(self, os_session, name, reservation, deploy_req_model):
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
        """

        # First create instance
        instance = self.instance_service.create_instance(os_session,
                                        name, reservation,
                                        deploy_request)

        # Get security groups For inbound/outbound ports
        sgs = self.instance_service.get_security_groups(os_session,
                                        instance)

        # Get Private IP

        # Populate all instance data

        # FIXME: generate DeployResultModel and return
