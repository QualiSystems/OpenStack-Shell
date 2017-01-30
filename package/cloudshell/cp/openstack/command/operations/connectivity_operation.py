from cloudshell.cp.openstack.domain.services.connectivity.vlan_connectivity_service import VLANConnectivityService


class ConnectivityOperation(object):
    public_ip = "Public IP"

    def __init__(self, connectivity_service):
        """

        :param connectivity_service:
        """
        self.connectivity_service = connectivity_service

    def apply_connectivity(self, openstack_session, cp_resource_model, conn_request, logger):
        """
        Implements Apply connectivity - parses the conn_requests and creates
        :param keystoneauth1.session.Session openstack_session:
        :param OpenStackResourceModel cp_resource_model:
        :param str conn_request: Connectivty Request JSON
        :param LoggingSessionContext logger:
        :return DriverResponseRoot:
        """

        return self.connectivity_service.\
            perform_apply_connectivity(openstack_session=openstack_session,
                                       cp_resource_model=cp_resource_model,
                                       connection_request=conn_request,
                                       logger=logger)
