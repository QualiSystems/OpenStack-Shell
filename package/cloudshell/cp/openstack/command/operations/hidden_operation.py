from cloudshell.cp.openstack.domain.services.nova.nova_instance_service import NovaInstanceService
from cloudshell.cp.openstack.domain.services.waiters.instance import InstanceWaiter


class HiddenOperation(object):
    def __init__(self):
        self.instance_waiter = InstanceWaiter()
        self.instance_service = NovaInstanceService(self.instance_waiter)

    def delete_instance(self, openstack_session, deployed_app_resource, floating_ip, logger):
        """
        Deletes the resource instance. Calls the instance_service method to terminate_instance

        :param keystoneauth1.session.Session openstack_session:
        :param DeployDataHolder deployed_app_resource:
        :param LoggingSessionContext logger:
        :param str floating_ip:
        :rtype None:
        """
        instance_id = deployed_app_resource.vmdetails.uid
        self.instance_service.terminate_instance(openstack_session=openstack_session,
                                                 instance_id=instance_id,
                                                 floating_ip=floating_ip,
                                                 logger=logger)
