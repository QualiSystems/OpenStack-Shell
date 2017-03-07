from neutronclient.v2_0 import client as neutron_client
from neutronclient.common.exceptions import Conflict as NetCreateConflict

import traceback
import time
import ipaddress

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
        :param logging.Logger logger:
        :return dict :
        """

        client = neutron_client.Client(session=openstack_session, insecure=True)

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
            request = {'network': create_nw_json}
            logger.info("Calling neutron client create_network with request: {}".format(request))
            new_net = client.create_network(request)
            new_net = new_net['network']
        except NetCreateConflict as e:
            logger.error(traceback.format_exc())
            networks_res = client.list_networks(**{'provider:segmentation_id': segmentation_id})
            networks = networks_res['networks']
            if not networks:
                logger.error("Network with segmentation id {0} not found and couldnt be created".format(segmentation_id))
                raise
            new_net = networks_res['networks'][0]

        logger.info("Got network: {}".format(new_net))

        return new_net

    def get_network_with_segmentation_id(self, openstack_session, segmentation_id, logger):
        """

        :param keystoneauth1.session.Session openstack_session:
        :param int segmentation_id:
        :param LoggingSessionContext logger:
        :return:
        """

        client = neutron_client.Client(session=openstack_session, insecure=True)

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
        :param logging.Logger logger:
        :return dict:
        """

        client = neutron_client.Client(session=openstack_session, insecure=True)

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

        request = {'subnet': create_subnet_json}
        logger.info("Calling neutron client create_subnet with request: {}".format(request))
        new_subnet = client.create_subnet(request)
        new_subnet = new_subnet['subnet']
        logger.info("Created new subnet: {}".format(new_subnet))

        return new_subnet

    def remove_subnet_and_net(self, openstack_session, network, logger):
        """

        :param keystoneauth1.session.Session openstack_session:
        :param dict network:
        :param logging.Logger logger:
        :return:
        """

        client = neutron_client.Client(session=openstack_session, insecure=True)

        try:
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

            logger.info("Found {0} ports: {1}".format(len(network_ports), network_ports))
            if len(network_ports) <= 1:
                for subnet in network['subnets']:
                    logger.info("Deleting subnet {}".format(subnet))
                    client.delete_subnet(subnet)

                logger.info("Deleting network {}".format(network))
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

        # We basically start with a 10.0. network to find a subnet that does not overlap with
        # either the reserved_cidrs or currently allocated CIDRs
        # currently supports /24 subnets
        logger.info("reserved CIDRs: {0}".format(cp_resvd_cidrs))

        # Empty reserved_addresses generates a list with single empty string
        blacklist_cidrs = filter(lambda x: len(x) > 0, map(lambda x: x.strip(), cp_resvd_cidrs.split(",")))

        current_subnets = client.list_subnets(fields=['cidr', 'id'])['subnets']
        current_subnets_cidrs = map(lambda x: unicode(x.get('cidr')), current_subnets)

        # Total CIDRs we don't care about are - reserved + currently allocated

        blacklist_cidrs += current_subnets_cidrs
        blacklist_cidrs = map(lambda x: unicode(x), blacklist_cidrs)
        logger.info("blacklist CIDRs: {0}".format(blacklist_cidrs))
        blacklist_subnets = map(lambda x: ipaddress.IPv4Network(x), blacklist_cidrs)

        # start with a 10 subnet
        found_subnet = None
        first_octet = 10
        for i in range(256):
            second_octet = i
            for j in range(256):
                third_octet = j
                subnet_str = '{0}.{1}.{2}.0/24'.format(first_octet, second_octet, third_octet)
                u_subnet_str = unicode(subnet_str)
                u_subnet = ipaddress.IPv4Network(u_subnet_str)
                # print u_subnet, blacklist_subnets
                if not any(map(lambda x: u_subnet.overlaps(x), blacklist_subnets)):
                    found_subnet = u_subnet
                    break
            if found_subnet:
                break

        if not found_subnet:
            first_octet = 172
            for i in range(16, 32):
                second_octet = i
                for j in range(256):
                    third_octet = j
                    subnet_str = '{0}.{1}.{2}.0/24'.format(first_octet, second_octet, third_octet)
                    u_subnet_str = unicode(subnet_str)
                    u_subnet = ipaddress.IPv4Network(u_subnet_str)
                    if not any(map(lambda x: u_subnet.overlaps(x), blacklist_subnets)):
                        found_subnet = u_subnet
                        break
                if found_subnet:
                    break

        if not found_subnet:
            first_octet = 192
            second_octet = 168
            for j in range(256):
                third_octet = j
                subnet_str = '{0}.{1}.{2}.0/24'.format(first_octet, second_octet, third_octet)
                u_subnet_str = unicode(subnet_str)
                u_subnet = ipaddress.IPv4Network(u_subnet_str)
                if not any(map(lambda x: u_subnet.overlaps(x), blacklist_subnets)):
                    found_subnet = u_subnet
                    break

        if not found_subnet:
            return None

        cidr = str(found_subnet)
        logger.info("Resolved CIDR: {}".format(cidr))

        return cidr


    def create_floating_ip(self, openstack_session, floating_ip_subnet_id, logger):
        """

        :param openstack_session:
        :param floating_ip_sunbet_id:
        :param logger:
        :return:
        """
        client = neutron_client.Client(session=openstack_session, insecure=True)

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

        client = neutron_client.Client(session=openstack_session, insecure=True)

        floating_ips_dict = client.list_floatingips(floating_ip_address=floating_ip)
        floating_ip_id = floating_ips_dict['floatingips'][0]['id']

        client.delete_floatingip(floating_ip_id)

        return True
