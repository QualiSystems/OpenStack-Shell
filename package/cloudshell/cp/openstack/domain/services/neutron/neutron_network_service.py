from neutronclient.v2_0 import client as neutron_client
from neutronclient.common.exceptions import Conflict as NetCreateConflict

import traceback
import time


class NeutronNetworkService(object):
    """
    A wrapper class around Neutron API
    """

    def __init__(self):
        self.cidr_base = None
        self.cidr_subnet_num = 0
        self.allocated_subnets = []

    def create_or_get_network_with_segmentation_id(self, openstack_session, cp_resource_model, segmentation_id, logger):
        """

        :param keystoneauth1.session.Session openstack_session:
        :param OpenStackResourceModel cp_resource_model:
        :param int segmentation_id:
        :param LoggingSessionContext logger:
        :return dict :
        """

        client = neutron_client.Client(session=openstack_session)

        interface_name = cp_resource_model.provider_network_interface
        network_type = cp_resource_model.vlan_type.lower()

        nw_name = "qs_net_segmentation_id_{0}".format(segmentation_id)
        create_nw_json = {'provider:network_type': network_type,
                              'provider:segmentation_id': segmentation_id,
                              'name': nw_name,
                              'admin_state_up': True}

        if network_type == 'vlan':
            create_nw_json.update({'provider:physical_network': interface_name})

        try:
            new_net = client.create_network({'network': create_nw_json})
            new_net = new_net['network']
        except NetCreateConflict as e:
            logger.error(traceback.format_exc())
            networks_res = client.list_networks(**{'provider:segmentation_id': segmentation_id})
            networks = networks_res['networks']
            if not networks:
                raise
            new_net = networks_res['networks'][0]

        return new_net

    def get_network_with_segmentation_id(self, openstack_session, segmentation_id, logger):
        """

        :param keystoneauth1.session.Session openstack_session:
        :param int segmentation_id:
        :param LoggingSessionContext logger:
        :return:
        """

        client = neutron_client.Client(session=openstack_session)

        net = client.list_networks(**{'provider:segmentation_id': segmentation_id})
        if net['networks']:
            return net['networks'][0]
        else:
            return None

    def create_and_attach_subnet_to_net(self, openstack_session, cp_resource_model, net_id, logger):
        """
        Atttach a subnet to the network with given net_id.

        :param keystoneauth1.session.Session openstack_session:
        :param OpenStackResourceModel cp_resource_model:
        :param str net_id: UUID string
        :return dict:
        """

        client = neutron_client.Client(session=openstack_session)

        cidr = self._get_unused_cidr(client=client, cp_resvd_cidrs=cp_resource_model.reserved_networks, logger=logger)
        if cidr is None:
            logger.error("Cannot allocate new subnet. All subnets exhausted")
            raise ValueError("All Subnets Exhausted")

        subnet_name = 'qs_subnet_' + net_id
        create_subnet_json = {'cidr': cidr,
                              'network_id': net_id,
                              'ip_version': 4,
                              'name': subnet_name,
                              'gateway_ip': None}

        new_subnet = client.create_subnet({'subnet':create_subnet_json})
        new_subnet = new_subnet['subnet']

        return new_subnet

    def remove_subnet_and_net(self, openstack_session, network, logger):
        """

        :param keystoneauth1.session.Session openstack_session:
        :param dict network:
        :param LoggingSessionContext logger:
        :return:
        """

        # FIXME: What happens if multiple threads call this?
        client = neutron_client.Client(session=openstack_session)

        try:
            #  FIXME: This whole block should be synchronized.

            # Get a list of all ports for this network. If there's any port with device owner other than DHCP,
            # You won't be able to delete the network or subnet. Retry it a few times (sometimes seen that when
            # this call happens, some 'ports' are still there.

            retries = 3
            network_ports = []
            while retries > 0:
                network_ports = client.list_ports(network_id=network['id'])['ports']
                if len(network_ports) > 1: # Wait and retry
                    retries -= 1
                    time.sleep(1)
                    continue
                else:
                    break

            logger.debug("Found {0} ports".format(network_ports))
            if len(network_ports) <= 1:
                for subnet in network['subnets']:
                    client.delete_subnet(subnet)

                client.delete_network(network['id'])

            else:
                logger.info("Some {0} ports with Associated IP still on Network. "
                            "Cannot delete network {1}".format(len(network_ports), network['id']))

        # FIXME: We should not be simply "Logging" here, take separate actions for each Exceptions
        # Network Not found : Ignore
        # Valid IPs still on Network: Raise
        # Any other: Raise to be on a safe side.
        except Exception:
            logger.error(traceback.format_exc())

    def _get_unused_cidr(self, client, cp_resvd_cidrs, logger):
        """
        Gets unused CIDR that excludes the reserved CIDRs

        :param neutronclient.v2_0.client:
        :param str cp_resvd_cidrs:
        :return str:
        """

        # Algorithm below is a very simplistic one where we choose one of the three prefixes and then use
        # /24 networks starting with that prefix. This algorithm will break if all three 10.X, 192.168.X and 172.X
        # networks are used in a given On Prem Network.

        logger.debug("reserved CIDRs: {0}".format(cp_resvd_cidrs))

        candidate_prefixes = {'10': '10.0', '192.168': '192.168', '172': '172.0'}
        cp_resvd_cidrs = cp_resvd_cidrs.split(",")
        possible_prefixes = filter(lambda x: any(map(lambda y: not y.strip().startswith(x), cp_resvd_cidrs)),
                                   candidate_prefixes.keys())
        logger.debug("Possible Prefixes that can be used: {0}".format(possible_prefixes))
        if not possible_prefixes:
            return None

        prefix = possible_prefixes[0]
        subnet_prefix = candidate_prefixes[prefix]

        # Get all subnets that start with 'our prefix'
        subnets = client.list_subnets(fields=['cidr', 'id'])['subnets']
        subnet_cidrs = map(lambda x: x.get('cidr'), subnets)

        allocated_subnets = []
        for subnet in subnets:
            if subnet['cidr'].startswith(prefix):
                allocated_subnets.append(subnet['cidr'])

        allocated_subnets.sort()
        logger.debug("Allocated Subnets: {0}".format(",".join(allocated_subnets)))

        if not allocated_subnets:
            subnet_num = 0
        else:
            last_subnet = allocated_subnets[-1]
            subnet_num = int(last_subnet.split("/")[0].split(".")[2])
            subnet_num += 1
        if subnet_num == 255:
            subnet_num = 0
            cidr = ".".join([subnet_prefix, str(subnet_num), "0/24"])
            while cidr in subnet_cidrs:
                subnet_num += 1
                cidr = ".".join([subnet_prefix, str(subnet_num), "0/24"])
        else:
            cidr = ".".join([subnet_prefix,str(subnet_num), "0/24"])

        logger.debug("Found {0} CIDR".format(cidr))

        if subnet_num == 255:
            return None

        return cidr

    def create_floating_ip(self, openstack_session, floating_ip_subnet_id, logger):
        """

        :param openstack_session:
        :param floating_ip_sunbet_id:
        :param logger:
        :return:
        """
        client = neutron_client.Client(session=openstack_session)

        # make sure subnet already exists
        subnet_dict = client.list_subnets(id=floating_ip_subnet_id)
        if not subnet_dict['subnets']:
            return None

        subnet = subnet_dict['subnets'][0]
        floating_network_id = subnet['network_id']

        floating_ip_create_dict = {'floatingip': {'floating_network_id': floating_network_id,
                                                  'subnet_id': floating_ip_subnet_id}}
        floating_ip = client.create_floatingip(floating_ip_create_dict)

        if floating_ip:
            return floating_ip['floatingip']
        else:
            return None

    def delete_floating_ip(self, openstack_session, floating_ip, logger):
        """

        :param openstack_session:
        :param floating_ip:
        :param logger:
        :return:
        """
        if not floating_ip:
            return False

        client = neutron_client.Client(session=openstack_session)

        floating_ips_dict = client.list_floatingips(floating_ip_address=floating_ip)
        floating_ip_id = floating_ips_dict['floatingips'][0]['id']

        client.delete_floatingip(floating_ip_id)

        return True