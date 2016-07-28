"""
Implements a concrete DeployOperation class.
"""

from cloudshell.cp.openstack.domain.services.nova.instance import InstanceService
from cloudshell.cp.openstack.domain.services.

class DeployOperation(object):
    def __init__(self):
        pass

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


