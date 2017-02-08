
class HiddenOperation(object):
    def __init__(self, instance_service, network_service):
        self.network_service = network_service
        self.instance_service = instance_service

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

        instance = self.instance_service.get_instance_from_instance_id(openstack_session=openstack_session,
                                                                       instance_id=instance_id,
                                                                       logger=logger)

        if floating_ip:
            if instance:
                self.instance_service.detach_floating_ip(openstack_session=openstack_session,
                                                         floating_ip=floating_ip,
                                                         instance=instance,
                                                         logger=logger)

            self.network_service.delete_floating_ip(openstack_session=openstack_session,
                                                    floating_ip=floating_ip,
                                                    logger=logger)

        if instance:
            self.instance_service.terminate_instance(openstack_session=openstack_session,
                                                 instance_id=instance_id,
                                                 logger=logger)
        else:
            logger.info("Instance with Instance ID Not found {}. Not deleting".format(instance_id))
