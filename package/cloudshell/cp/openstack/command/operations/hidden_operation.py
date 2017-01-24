from cloudshell.cp.openstack.domain.services.nova.nova_instance_service import NovaInstanceService
from cloudshell.cp.openstack.domain.services.waiters.instance import InstanceWaiter


class HiddenOperation(object):
    def __init__(self, cancellation_service):
        self.instance_waiter = InstanceWaiter(cancellation_service=cancellation_service)
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
                                                 logger=logger)

        if floating_ip:
            self.instance_service.delete_floating_ip(openstack_session=openstack_session, floating_ip=floating_ip)
