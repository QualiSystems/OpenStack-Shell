from cloudshell.cp.openstack.domain.services.nova.nova_instance_service import NovaInstanceService
from cloudshell.cp.openstack.domain.services.waiters.instance import InstanceWaiter


class HiddenOperation(object):
    def __init__(self):
        self.instance_waiter = InstanceWaiter()
        self.instance_service = NovaInstanceService(self.instance_waiter)

    def delete_instance(self, openstack_session, deployed_app_resource, logger):
        """
        Deletes the resource instance. Calls the instance_service method to terminate_instance

        :param openstack_session:
        :type openstack_session:
        :param deployed_app_resource:
        :type deployed_app_resource:
        :param logger:
        :type logger:
        :return:
        """
        instance_id = deployed_app_resource.vmdetails.uuid
        self.instance_service.terminate_instance(openstack_session=openstack_session,
                                                 instance_id=instance_id,
                                                 logger=logger)
        pass
