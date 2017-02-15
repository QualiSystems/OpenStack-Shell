
from cloudshell.shell.core.driver_context import AutoLoadDetails

from novaclient import client as nova_client
from neutronclient.v2_0 import client as neutron_client
from keystoneclient import client as keystone_client

import keystoneauth1.exceptions
import novaclient.exceptions

import ipaddress
import traceback


class OpenStackCPValidator(object):

    def __init__(self):
        pass

    def validate_controller_url(self, controller_url, logger):

        return self._is_not_empty(controller_url, "Controller URL") and \
               self._is_http_url(controller_url, "Controller URL")

    def validate_openstack_domain(self, os_domain, logger):

        return self._is_not_empty(os_domain, "OpenStack Domain")

    def validate_openstack_project(self, os_project, logger):

        return self._is_not_empty(os_project, "OpenStack Project")

    def validate_openstack_username(self, os_username, logger):

        return self._is_not_empty(os_username, "OpenStack Username")

    def validate_openstack_password(self, os_password, logger):

        return self._is_not_empty(os_password, "OpenStack Passwrd")

    def _is_not_empty(self, value, err_value):

        if len(value) == 0:
            raise ValueError("{0} Cannot be empty".format(err_value))

        return True

    def _is_http_url(self, value, err_value):

        if not (value.lower().startswith('http://') or value.lower().startswith('https://')):
            raise ValueError("{0} {1} is not in valid format.".format(err_value, value))

        return True

    def _get_network_from_id(self, net_client, network_id):

        try:
            net_list = net_client.list_networks(id=network_id)

            #empty list
            if not net_list['networks']:
                raise ValueError("Network with ID {0} Not Found".format(network_id))

            if len(net_list['networks']) != 1:
                raise ValueError("More than one network matching ID {0} Found".format(network_id))
            network_obj = net_list['networks'][0]

        except ValueError:
            raise

        except Exception as e:
            raise ValueError("Unhandled Exception Occurred. {0}".format(e))

        return network_obj

    def validate_mgmt_network(self, net_client, mgmt_network_id, logger):

        # we do not wrap this in try because we assume - we have validated credentials already

        if len(mgmt_network_id) == 0:
            raise ValueError("OpenStack Management Network ID Cannot be empty")

        _ = self._get_network_from_id(net_client, mgmt_network_id)

        return True

    def validate_floating_ip_subnet(self, net_client, floating_ip_subnet_id, logger):

        if len(floating_ip_subnet_id) == 0:
            raise ValueError("Floating IP Subnet ID Cannot be Empty")

        subnet = net_client.show_subnet(floating_ip_subnet_id)

        external_network_id = subnet['subnet']['network_id']
        external_network = self._get_network_from_id(net_client, external_network_id)

        if not external_network['router:external']:
            raise ValueError("Network with ID {0} exists but is not an external network.".format(external_network_id))

        return True

    def validate_vlan_type(self, net_client, vlan_type, provider_net_interface, logger):

        vlan_type = vlan_type.lower()
        if vlan_type not in ['vlan', 'vxlan']:
            raise ValueError("Vlan Type should be one of \"VLAN\" or \"VXLAN\".")

        try:

            create_nw_json = {'provider:network_type': vlan_type,
                              'name': 'qs_autoload_validation_net',
                              'provider:segmentation_id': 42,
                              'admin_state_up': True}

            if vlan_type == 'vlan':
                create_nw_json.update({'provider:physical_network': provider_net_interface})

            network_dict = net_client.create_network({'network': create_nw_json})
            net_client.delete_network(network_dict['network']['id'])

        except Exception as e:
            raise ValueError("Error occurred during creating network. {0}".format(e))

        return True

    def validate_reserved_networks(self, reserved_networks, logger):

        # Just try to create an IPv4Network if anything, it'd raise a ValueError
        for reserved_net in reserved_networks.split(","):
            if len(reserved_net) == 0:
                continue
            ipaddress.ip_network(unicode(reserved_net.strip()))

        return True

    def validate_region(self, openstack_session, cs_session, cp_resource_model, logger):
        """

        :param openstack_session:
        :param cs_session:
        :param cp_resource_model:
        :param logger:
        :return:
        """

        region_name = cp_resource_model.os_region
        if len(region_name) == 0:
            # Empty region allowed - Do nothing
            return True

        try:
            ks_client = keystone_client.Client(session=openstack_session)
            ks_client.regions.get(region_name)

        except keystoneauth1.exceptions.http.NotFound:
            raise

        except Exception as e:
            raise ValueError("Unknown Error occurred trying to get Region with id {0}. Error: {1}".
                             format(region_name, e))
        return True

    def validate_network_attributes(self, openstack_session, cp_resource_model, logger):
        """

        :param openstack_session:
        :param cp_resource_model:
        :param logger:
        :return:
        """
        net_client = neutron_client.Client(session=openstack_session)

        self.validate_mgmt_network(net_client, cp_resource_model.qs_mgmt_os_net_uuid, logger)

        self.validate_floating_ip_subnet(net_client, cp_resource_model.floating_ip_subnet_uuid, logger)

        self.validate_vlan_type(net_client=net_client,
                                vlan_type=cp_resource_model.vlan_type,
                                provider_net_interface=cp_resource_model.provider_network_interface,
                                logger=logger)

        self.validate_reserved_networks(cp_resource_model.reserved_networks, logger)

    def validate_openstack_credentials(self, openstack_session, cs_session, cp_resource_model, logger):
        """

        :param openstack_session:
        :param cs_session:
        :param cp_resource_model:
        :param logger:
        :return:
        """

        if not self.validate_controller_url(cp_resource_model.controller_url, logger):
            return False

        if not self.validate_openstack_domain(cp_resource_model.os_domain_name, logger):
            return False

        if not self.validate_openstack_project(cp_resource_model.os_project_name, logger):
            return False

        if not self.validate_openstack_username(cp_resource_model.os_user_name, logger):
            return False

        os_user_passwd = cs_session.DecryptPassword(cp_resource_model.os_user_password).Value
        if not self.validate_openstack_password(os_user_passwd, logger):
            return False

        try:
            compute_client = nova_client.Client(version='2.0', session=openstack_session)
            # An API Call to Validate Credentials
            _ = compute_client.servers.list()

        except keystoneauth1.exceptions.http.BadRequest:
            # Empty user domain or project domain
            raise

        except keystoneauth1.exceptions.http.Unauthorized:
            # invalid domain name or user name password - let user know explicitly
            raise

        except keystoneauth1.exceptions.http.NotFound:
            # Contorller URL not not valid
            logger.error(traceback.format_exc())
            raise ValueError("Controller URL '{}' is not found".format(cp_resource_model.controller_url))

        except Exception as e:
            logger.error(traceback.format_exc())
            raise ValueError("One or more values are not correct. {0}".format(e.message))

        return True

    def validate_all(self, openstack_session, cs_session, cp_resource_model, logger):
        """

        :param openstack_session:
        :param cs_session:
        :param cp_resource_model:
        :param logger:
        :return:
        """

        self.validate_openstack_credentials(openstack_session=openstack_session,
                                            cs_session=cs_session,
                                            cp_resource_model=cp_resource_model,
                                            logger=logger)

        self.validate_network_attributes(openstack_session=openstack_session,
                                         cp_resource_model=cp_resource_model,
                                         logger=logger)

        return AutoLoadDetails([], [])
