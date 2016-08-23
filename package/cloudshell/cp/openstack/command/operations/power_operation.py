from cloudshell.cp.openstack.domain.services.nova.nova_instance_service import NovaInstanceService
from cloudshell.cp.openstack.domain.services.waiters.instance import InstanceWaiter

class PowerOperation(object):
    def __init__(self):
        self.instance_waiter = InstanceWaiter()
        self.instance_service = NovaInstanceService(self.instance_waiter)

    def power_on(self, openstack_session, cloudshell_session,
                 deployed_app_resource, resource_fullname,
                 logger):
        """
        Powers on a given instance from the deployed_app_resource

        :param openstack_session:
        :type openstack_session:
        :param cloudshell_session:
        :type cloudshell_session:
        :param deployed_app_resource:
        :type deployed_app_resource:
        :param resource_fullname:
        :type resource_fullname:
        :param logger:
        :type logger:
        :return:
        """

        instance_id = deployed_app_resource.vmdetails.uid
        try:
            self.instance_service.instance_power_on(openstack_session=openstack_session,
                                                    instance_id=instance_id,
                                                    logger=logger)
            cloudshell_session.SetResourceLiveStatus(resource_fullname, "Online", "Active")
        except Exception as e:
            # We ignore errors
            cloudshell_session.SetResourceLiveStatus(resource_fullname, "Error", "Error")
            logger.debug("Exception {0} occurred, while trying to power on instance".format(e.message))

    def power_off(self, openstack_session, cloudshell_session,
                 deployed_app_resource, resource_fullname,
                 logger):
        """
        Powers down a given instance (obtained from deployed_app_resource.vmdetails.uid

        :param openstack_session:
        :type openstack_session:
        :param cloudshell_session:
        :type cloudshell_session:
        :param deployed_app_resource:
        :type deployed_app_resource:
        :param resource_fullname:
        :type resource_fullname:
        :param logger:
        :type logger:
        :return:
        """

        # FIXME : add details
        instance_id = deployed_app_resource.vmdetails.uid
        try:
            self.instance_service.instance_power_off(openstack_session=openstack_session,
                                                    instance_id=instance_id,
                                                    logger=logger)
            cloudshell_session.SetResourceLiveStatus(resource_fullname, "Offline", "Powered Off")
        except Exception as e:
            # We ignore errors
            cloudshell_session.SetResourceLiveStatus(resource_fullname, "Error", "Error")
            logger.debug("Exception {0} occurred, while trying to power off instance".format(e.message))
