from cloudshell.shell.core.session.logging_session import LoggingSessionContext

import traceback


class PowerOperation(object):
    def __init__(self, instance_service):
        self.instance_service = instance_service

    def power_on(self, openstack_session, cloudshell_session,
                 deployed_app_resource, resource_fullname,
                 logger):
        """
        Powers on a given instance from the deployed_app_resource

        :param keystoneauth1.session.Session openstack_session:
        :param CloudShellSessionContext cloudshell_session:
        :param DeployDataHolder deployed_app_resource:
        :param str resource_fullname:
        :param LoggingSessionContext logger:
        :rtype None:
        """

        instance_id = deployed_app_resource.vmdetails.uid
        try:
            self.instance_service.instance_power_on(openstack_session=openstack_session,
                                                    instance_id=instance_id,
                                                    logger=logger)
            cloudshell_session.SetResourceLiveStatus(resource_fullname, "Online", "Active")
        except Exception as e:
            cloudshell_session.SetResourceLiveStatus(resource_fullname, "Error", e.message)
            logger.error(traceback.format_exc())
            raise # reraise the exception

    def power_off(self, openstack_session, cloudshell_session,
                 deployed_app_resource, resource_fullname,
                 logger):
        """
        Powers down a given instance (obtained from deployed_app_resource.vmdetails.uid

        :param keystoneauth1.session.Session openstack_session:
        :param CloudShellSessionContext cloudshell_session:
        :param DeployDataHolder deployed_app_resource:
        :param str resource_fullname:
        :param LoggingSessionContext logger:
        :rtype None:
        """

        # FIXME : add details
        instance_id = deployed_app_resource.vmdetails.uid
        try:
            self.instance_service.instance_power_off(openstack_session=openstack_session,
                                                    instance_id=instance_id,
                                                    logger=logger)
            cloudshell_session.SetResourceLiveStatus(resource_fullname, "Offline", "Powered Off")
        except Exception as e:
            cloudshell_session.SetResourceLiveStatus(resource_fullname, "Error", e.message)
            logger.error(traceback.format_exc())
            raise  # Reraise the exception