
class ConnectivityOperation(object):
    def __init__(self):
        pass

    def refresh_ip(self, openstack_session, cloudshell_session, deployed_app_resource, logger):
        """

        :param openstack_session:
        :type openstack_session:
        :param cloudshell_session:
        :type cloudshell_session:
        :param deployed_app_resource:
        :type deployed_app_resource:
        :param logger:
        :type logger:
        :return:
        """
        logger.info("Refresh_IP called")
