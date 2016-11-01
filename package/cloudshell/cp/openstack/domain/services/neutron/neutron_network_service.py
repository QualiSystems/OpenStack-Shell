from neutronclient.v2_0 import client as neutron_client
from neutronclient.common.exceptions import Conflict as NetCreateConflict

class NeutronNetworkService(object):
    """
    A wrapper class around Neutron API
    """

    def __init__(self):
        self.cidr_base = None
        self.cidr_subnet_num = 0
        self.allocated_subnets = []

    def create_network_with_vlanid(self, openstack_session, vlanid, logger):
        """

        :param keystoneauth1.session.Session openstack_session:
        :param int vlanid:
        :param LoggingSessionContext logger:
        :return dict :
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
        except NetCreateConflict:
            new_net = client.list_networks(**{'provider:segmentation_id':vlanid})
            new_net = new_net['networks'][0]
        except Exception as e:
            logger.error("Exception {0} Occurred while creating network".format(e))
            return None

        return new_net

    def attach_subnet_to_net(self, openstack_session, cp_resource_model, net_id, logger):
        """
        Atttach a subnet to the network with given net_id.

        :param keystoneauth1.session.Session openstack_session:
        :param OpenStackResourceModel cp_resource_model:
        :param str net_id: UUID string
        :return dict:
        """

        client = neutron_client.Client(session=openstack_session)

        cidr = self._get_unused_cidr(cp_resvd_cidrs=cp_resource_model.reserved_networks, logger=logger)
        if cidr is None:
            logger.error("Cannot allocate new subnet. All subnets exhausted")
            return None

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

    def _get_unused_cidr(self, cp_resvd_cidrs, logger):
        """
        Gets unused CIDR that excludes the reserved CIDRs
        :param str cp_resvd_cidrs:
        :return str:
        """

        # Algorithm below is a very simplistic one where we choose one of the three prefixes and then use
        # /24 networks starting with that prefix. This algorithm will break if all three 10.X, 192.168.X and 172.X
        # networks are used in a given On Prem Network.
        if self.cidr_base is not None:
            cidr = ".".join([self.cidr_base, str(self.cidr_subnet_num), "0/24"])
            if self.cidr_subnet_num not in self.allocated_subnets:
                self.allocated_subnets.append(self.cidr_subnet_num)
                self.cidr_subnet_num += 1
                if self.cidr_subnet_num == 255:
                    self.cidr_subnet_num = 0
                return cidr
        else:
            candidate_prefixes = {'10': '10.0', '192.168': '192.168', '172': '172.0'}
            cp_resvd_cidrs = cp_resvd_cidrs.split(",")
            logger.error(cp_resvd_cidrs)
            possible_prefixes = filter(lambda x: any(map(lambda y: not y.strip().startswith(x), cp_resvd_cidrs)),
                                       candidate_prefixes.keys())

            logger.info(possible_prefixes)
            if not possible_prefixes:
                return None
            else:
                prefix = possible_prefixes[0]
                self.cidr_base = candidate_prefixes[prefix]
                cidr = ".".join([self.cidr_base, str(self.cidr_subnet_num), "0/24"])
                self.allocated_subnets.append(self.cidr_subnet_num)
                self.cidr_subnet_num += 1
                return cidr
        return None