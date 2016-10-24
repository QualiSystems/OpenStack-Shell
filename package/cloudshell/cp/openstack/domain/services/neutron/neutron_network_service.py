from neutronclient.v2_0 import client as neutron_client

class NeutronNetworkService(object):
    """
    A wrapper class around Neutron API
    """

    def __init__(self):
        pass
        self.cidr_octet3 = 0
        self.cidr_str = '10.1.{0}.0/24'

    def create_network_with_vlanid(self, openstack_session, vlanid, logger):
        """

        :param openstack_session:
        :param vlanid:
        :return:
        """

        client = neutron_client.Client(session=openstack_session)

        nw_name = "net_vlanid_{0}".format(vlanid)
        create_nw_json = {'provider:physical_network': 'public',
                          'provider:network_type': 'vlan',
                          'provider:segmentation_id': vlanid,
                          'name': nw_name,
                          'admin_state_up': True}

        # FIXME : If an exception is raised - we just raise it all the way back? For now yes
        try:
            new_net = client.create_network({'network': create_nw_json})
            new_net = new_net['network']
        except Exception as e:
            logger.error("Exception {0} Occurred while creating network".format(e))
            return None

        return new_net

    def attach_subnet_to_net(self, openstack_session, net_id, logger):
        """

        :param net_id:
        :return:
        """

        client = neutron_client.Client(session=openstack_session)

        # FIXME: would work for 255 networks only for now
        cidr = self.cidr_str.format(self.cidr_octet3)
        self.cidr_octet3 += 1

        create_subnet_json = {'cidr': cidr,
                              'network_id': net_id,
                              'ip_version': 4}

        try:
            new_subnet = client.create_subnet({'subnet':create_subnet_json})
            new_subnet = new_subnet['subnet']
        except Exception as e:
            logger.error("Exception {0} Occurred while creating network".format(e))
            return None

        return new_subnet
