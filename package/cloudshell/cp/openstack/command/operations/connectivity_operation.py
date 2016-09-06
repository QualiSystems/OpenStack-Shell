from cloudshell.cp.openstack.domain.services.nova.nova_instance_service import NovaInstanceService
from cloudshell.cp.openstack.domain.services.waiters.instance import InstanceWaiter

class ConnectivityOperation(object):
    public_ip = "Public IP"

    def __init__(self):
        self.instance_waiter = InstanceWaiter()
        self.instance_service = NovaInstanceService(self.instance_waiter)

    def refresh_ip(self, openstack_session, cloudshell_session,
                   deployed_app_resource, private_ip, resource_fullname,
                   logger):
        """

        :param keystoneauth1.session.Session openstack_session:
        :param CloudShellSessionContext cloudshell_session:
        :param deployed_app_resource:
        :param str private_ip:
        :param str resource_fullname:
        :param LoggingSessionContext logger:
        :rtype None:
        """
        logger.info(deployed_app_resource.attributes)
        logger.info(private_ip)
        logger.info("Refresh_IP called")

        instance_id = deployed_app_resource.vmdetails.uid
        instance = self.instance_service.get_instance_from_instance_id(openstack_session=openstack_session,
                                                                       instance_id=instance_id)
        if instance is None:
            raise ValueError("Instance with InstanceID {0} not found".format(instance_id))

        new_private_ip = self.instance_service.get_private_ip(instance)
        if new_private_ip != private_ip:
            cloudshell_session.UpdateResourceAddress(resource_fullname, new_private_ip)

        # FIXME : hardcoded public IP right now. Get it from floating IP later.
        cloudshell_session.SetAttributeValue(resource_fullname, ConnectivityOperation.public_ip, "192.168.1.1")
