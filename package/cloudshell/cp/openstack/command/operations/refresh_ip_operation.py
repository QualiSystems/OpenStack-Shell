
from cloudshell.cp.openstack.domain.services.nova.nova_instance_service import NovaInstanceService
from cloudshell.cp.openstack.domain.services.waiters.instance import InstanceWaiter


class RefreshIPOperation(object):
    public_ip = "Public IP"

    def __init__(self, instance_service):
        self.instance_service = instance_service

    def refresh_ip(self, openstack_session, cloudshell_session,
                   deployed_app_resource, private_ip,
                   resource_fullname, cp_resource_model, logger):
        """

        :param keystoneauth1.session.Session openstack_session:
        :param CloudShellSessionContext cloudshell_session:
        :param deployed_app_resource:
        :param str private_ip:
        :param str resource_fullname:
        :param OpenStackResourceModel cp_resource_model:
        :param LoggingSessionContext logger:
        :rtype None:
        """
        logger.debug(deployed_app_resource)
        logger.info(deployed_app_resource.attributes)
        logger.info(private_ip)
        logger.info("Refresh_IP called")

        instance_id = deployed_app_resource.vmdetails.uid
        instance = self.instance_service.get_instance_from_instance_id(openstack_session=openstack_session,
                                                                       instance_id=instance_id,
                                                                       logger=logger)
        if instance is None:
            raise ValueError("Instance with InstanceID {0} not found".format(instance_id))

        private_network_name = self.instance_service.get_instance_mgmt_network_name(instance=instance,
                                                                                    openstack_session=openstack_session,
                                                                                    cp_resource_model=cp_resource_model)
        if private_network_name is None:
            raise ValueError("Management network with ID for instance not found".\
                                format(cp_resource_model.qs_mgmt_os_net_id))
        new_private_ip = self.instance_service.get_private_ip(instance, private_network_name)
        if new_private_ip != private_ip:
            cloudshell_session.UpdateResourceAddress(resource_fullname, new_private_ip)
