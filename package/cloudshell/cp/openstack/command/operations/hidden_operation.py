from cloudshell.cp.openstack.domain.services.nova.nova_instance_service import NovaInstanceService
from cloudshell.cp.openstack.domain.services.waiters.instance import InstanceWaiter


class HiddenOperation(object):
    def __init__(self):
        self.instance_waiter = InstanceWaiter()
        self.instance_service = NovaInstanceService(self.instance_waiter)

    def delete_instance(self, deployed_app_resource):
        """
        Deletes the Given OpenStack instance.
        :param deployed_app_resource:
        :return:
        """
        pass
