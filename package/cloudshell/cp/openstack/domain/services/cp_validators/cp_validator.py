
from cloudshell.core.logger.qs_logger import get_qs_logger

from cloudshell.cp.openstack.common.driver_helper import CloudshellDriverHelper
from cloudshell.cp.openstack.models.model_parser import OpenStackShellModelParser
from cloudshell.cp.openstack.domain.services.session_providers.os_session_provider import OpenStackSessionProvider

from novaclient import client as nova_client
from neutronclient.v2_0 import client as neutron_client
from keystoneclient import client as keystone_client

import keystoneauth1.exceptions
import novaclient.exceptions

import ipaddress
import traceback


class OpenStackCPValidator(object):

    def __init__(self, context):

        # Get CP Resource Object
        self.model_parser = OpenStackShellModelParser()
        self.cp_resource = self.model_parser.get_resource_model_from_context(context.resource)

        # Get Logger
        logger = get_qs_logger(log_group='Autoload',
                               log_file_prefix=context.resource.name,
                               log_category="OpenStackShell")
        self.logger = logger

        # Get CloudShell Sesssion
        cs_domain = 'Global'
        cs_helper = CloudshellDriverHelper()
        self.cs_session = cs_helper.get_session(server_address=context.connectivity.server_address,
                                                token=context.connectivity.admin_auth_token,
                                                reservation_domain=cs_domain)

        # Get OpenStack Session Object
        os_session_provider = OpenStackSessionProvider()
        self.os_session = os_session_provider.get_openstack_session(cloudshell_session=self.cs_session,
                                                                    openstack_resource_model=self.cp_resource,
                                                                    logger=logger)

    def validate_controller_url(self, controller_url):

        if len(controller_url) == 0:
            raise ValueError("Controller URL Cannot be empty.")

        if not ( controller_url.lower().startswith('http://') or
                 controller_url.lower().startswith('https://')):
            raise ValueError("Controller URL {0} is not in valid format.".format(controller_url))

        return True

    def validate_openstack_domain(self, os_domain):

        if len(os_domain) == 0:
            raise ValueError("OpenStack Domain Cannot be empty")

        return True

    def validate_openstack_project(self, os_project):

        if len(os_project) == 0:
            raise ValueError("OpenStack Project Cannot be empty")

        return True

    def validate_openstack_username(self, os_username):

        if len(os_username) == 0:
            raise ValueError("OpenStack User cannot be empty")

        return True

    def validate_openstack_password(self, os_password):

        if len(os_password) == 0:
            return ValueError("OpenStack Password cannot be empty")

        return True

    def _get_network_from_id(self, net_client, network_id):

        try:
            net_list = net_client.list_networks(id=network_id)

            #empty list
            if not net_list['networks']:
                raise ValueError("Network with ID {0} Not Found".format(network_id))

            if len(net_list['networks']) != 1:
                raise ValueError("More than one network matching ID {0} Found".format(network_id
                                                                                      ))
            network_obj = net_list['networks'][0]

        except ValueError:
            raise

        except Exception as e:
            raise ValueError("Unhandled Exception Occurred. {0}".format(e))

        return network_obj

    def validate_mgmt_network(self, net_client, mgmt_network_id):

        # we do not wrap this in try because we assume - we have validated credentials already

        if len(mgmt_network_id) == 0:
            raise ValueError("Quali Management Network UUID Cannot be empty")

        _ = self._get_network_from_id(net_client, mgmt_network_id)

        return True

    def validate_external_network(self, net_client, external_network_id):

        if len(external_network_id) == 0:
            raise ValueError("External Network UUID Cannot be Empty")

        external_network = self._get_network_from_id(net_client, external_network_id)

        if not external_network['router:external']:
            raise ValueError("Network with ID {0} exists but is not an external network.".format(external_network_id))

        return True

    def validate_vlan_type(self, net_client, vlan_type, provider_net_interface):

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

    def validate_reserved_networks(self, reserved_networks):

        # Just try to create an IPv4Network if anything, it'd raise a ValueError
        for reserved_net in reserved_networks.split(","):
            if len(reserved_net) == 0:
                continue
            ipaddress.ip_network(unicode(reserved_net))

        return True

    def validate_region(self):

        region_name = self.cp_resource.os_region
        if len(region_name) == 0:
            # Empty region allowed - Do nothing
            return True

        try:
            ks_client = keystone_client.Client(session=self.os_session)
            ks_client.regions.get(region_name)

        except keystoneauth1.exceptions.http.NotFound:
            raise

        except Exception as e:
            raise ValueError("Unknown Error occurred trying to get Region with id {0}. Error: {1}".
                             format(region_name, e))

    def validate_network_attributes(self):

        net_client = neutron_client.Client(session=self.os_session)
        self.validate_mgmt_network(net_client, self.cp_resource.qs_mgmt_os_net_uuid)
        self.validate_external_network(net_client, self.cp_resource.external_network_uuid)
        self.validate_vlan_type(net_client=net_client,
                                vlan_type=self.cp_resource.vlan_type,
                                provider_net_interface=self.cp_resource.provider_network_interface)
        self.validate_reserved_networks(self.cp_resource.reserved_networks)

    def validate_openstack_credentials(self):

        if not self.validate_controller_url(self.cp_resource.controller_url):
            return False

        if not self.validate_openstack_domain(self.cp_resource.os_domain_name):
            return False

        if not self.validate_openstack_project(self.cp_resource.os_project_name):
            return False

        if not self.validate_openstack_username(self.cp_resource.os_user_name):
            return False

        os_user_passwd = self.cs_session.DecryptPassword(self.cp_resource.os_user_password).Value
        if not self.validate_openstack_password(os_user_passwd):
            return False

        try:
            compute_client = nova_client.Client(version='2.0', session=self.os_session)
            # An API Call to Validate Credentials
            _ = compute_client.servers.list()

        except keystoneauth1.exceptions.http.BadRequest:
            # Empty user domain or project domain
            raise

        except keystoneauth1.exceptions.http.Unauthorized:
            # invalid domain name or user name password - let user know explicitly
            raise

        except keystoneauth1.exceptions.http.NotFound:
            raise

        except Exception as e:
            self.logger.error(traceback.format_exc())
            raise ValueError("One or more values are not correct. {0}".format(e.message))

        return True

    def validate_all(self):

        self.validate_openstack_credentials()

        self.validate_region()

        self.validate_network_attributes()
