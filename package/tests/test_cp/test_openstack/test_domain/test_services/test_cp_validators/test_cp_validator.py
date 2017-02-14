from unittest import TestCase
from mock import Mock

import cloudshell.cp.openstack.domain.services.cp_validators.cp_validator as test_cp_validator
from cloudshell.cp.openstack.models.openstack_resource_model import OpenStackResourceModel
from cloudshell.cp.openstack.domain.services.cp_validators.cp_validator import OpenStackCPValidator


class TestOpenStackSessionProvider(TestCase):
    def setUp(self):
        self.mock_logger = Mock()
        self.cp_validator = OpenStackCPValidator()

    def test_validate_controller_url_empty_url(self):
        test_empty_url = ''
        with self.assertRaises(ValueError) as context:
            self.cp_validator.validate_controller_url(test_empty_url, self.mock_logger)

        self.assertTrue(context)

    def test_validate_empty_url_not_start_with_http(self):
        test_nohttp_url = 'test'

        with self.assertRaises(ValueError) as context:
            self.cp_validator.validate_controller_url(test_nohttp_url, self.mock_logger)

        self.assertTrue(context)

    def test_valid_controller_url(self):
        valid_url = 'http://example.com:5000'

        self.assertTrue(self.cp_validator.validate_controller_url(valid_url, self.mock_logger))

    def test_invalid_vlan_type(self):
        test_net_client = Mock()
        test_vlan_type = 'test'
        test_provider_net_interface = 'test_interface'

        with self.assertRaises(ValueError) as context:
            self.cp_validator.validate_vlan_type(net_client=test_net_client,
                                                 vlan_type=test_vlan_type,
                                                 provider_net_interface=test_provider_net_interface,
                                                 logger=self.mock_logger)
        self.assertTrue(context)

    def test_validate_vlan_type_success(self):
        test_net_client = Mock()

        test_net_client.create_network = Mock(return_value={'network': {'id': 'test_id'}})
        test_net_client.delete_network = Mock()

        test_vlan_type = 'vlan'
        test_provider_net_interface = 'test_interface'

        result = self.cp_validator.validate_vlan_type(net_client=test_net_client,
                                                      vlan_type=test_vlan_type,
                                                      provider_net_interface=test_provider_net_interface,
                                                      logger=self.mock_logger)
        self.assertTrue(result)

    def test_validate_vlan_type_exception(self):
        test_net_client = Mock()

        test_net_client.create_network = Mock(side_effect=Exception)
        test_net_client.delete_network = Mock()

        test_vlan_type = 'vlan'
        test_provider_net_interface = 'test_interface'

        with self.assertRaises(Exception) as context:
            self.cp_validator.validate_vlan_type(net_client=test_net_client,
                                                 vlan_type=test_vlan_type,
                                                 provider_net_interface=test_provider_net_interface,
                                                 logger=self.mock_logger)
        self.assertTrue(context)

    def test_validate_floating_ip_subnet(self):
        test_net_client = Mock()

        test_network_id = 'test_network_id'
        mock_subnet_result = {'subnet': {'network_id': test_network_id}}
        test_net_client.show_subnet = Mock(return_value=mock_subnet_result)

        test_floating_ip_subnet_id = 'test_floating_ip_subnet'

        net_list = {'networks': [{'router:external': True}]}
        test_net_client.list_networks = Mock(return_value=net_list)

        result = self.cp_validator.validate_floating_ip_subnet(net_client=test_net_client,
                                                               floating_ip_subnet_id=test_floating_ip_subnet_id,
                                                               logger=self.mock_logger)

        self.assertTrue(result)

    def test_validate_external_network_exception(self):
        test_net_client = Mock()

        test_net_client.show_subnet = Mock(side_effect=Exception)

        test_floating_ip_subnet_id = 'test_external_net'

        with self.assertRaises(Exception) as context:
            self.cp_validator.validate_floating_ip_sunbet(net_client=test_net_client,
                                                          floating_ip_subnet_id=test_floating_ip_subnet_id,
                                                          logger=self.mock_logger)

        self.assertTrue(context)

    def test_validate_mgmt_network(self):
        test_net_client = Mock()

        net_list = {'networks': [{'router:external': False}]}
        test_net_client.list_networks = Mock(return_value=net_list)

        test_mgmt_network_id = 'test_mgmt_net'
        result = self.cp_validator.validate_mgmt_network(net_client=test_net_client,
                                                         mgmt_network_id=test_mgmt_network_id,
                                                         logger=self.mock_logger)

        self.assertTrue(result)

    def test_validate_network_attributes(self):
        mock_cp_resource_model = Mock()
        mock_cp_resource_model.qs_mgmt_os_net_uuid = 'test-mgmt-uuid'
        mock_cp_resource_model.floating_ip_subnet_uuid = 'test-subnet-uuid'
        mock_cp_resource_model.vlan_type = 'vlan'
        mock_cp_resource_model.reserved_networks = 'reserved-networks'
        mock_cp_resource_model.provider_network_interface = 'test-if'

        mock_os_session = Mock()

        mock_net_client = Mock()
        test_cp_validator.neutron_client = Mock()
        test_cp_validator.neutron_client.Client = Mock(return_value=mock_net_client)

        self.cp_validator.validate_mgmt_network = Mock(return_value=True)
        self.cp_validator.validate_floating_ip_subnet = Mock(return_value=True)
        self.cp_validator.validate_vlan_type = Mock(return_value=True)
        self.cp_validator.validate_reserved_networks = Mock(return_value=True)

        self.cp_validator.validate_network_attributes(openstack_session=mock_os_session,
                                                      cp_resource_model=mock_cp_resource_model,
                                                      logger=self.mock_logger)

        self.cp_validator.validate_floating_ip_subnet.assert_called_with(mock_net_client, 'test-subnet-uuid',
                                                                         self.mock_logger)
        self.cp_validator.validate_mgmt_network.assert_called_with(mock_net_client, 'test-mgmt-uuid',
                                                                   self.mock_logger)
        self.cp_validator.validate_vlan_type.assert_called_with(net_client=mock_net_client, vlan_type='vlan',
                                                                provider_net_interface='test-if',
                                                                logger=self.mock_logger)
        self.cp_validator.validate_reserved_networks.assert_called_with('reserved-networks', self.mock_logger)

    def test_validate_openstack_credentials(self):
        mock_openstack_sesion = Mock()
        mock_cs_session = Mock()
        mock_cp_resource_model = Mock()

        mock_passwd = Mock()
        mock_passwd.Value = 'mock-passwd'
        mock_cs_session.DecryptPassword = Mock(return_value=mock_passwd)

        mock_nova_client = Mock()
        mock_nova_client.servers = Mock()
        mock_nova_client.servers.list = Mock(return_type=[])
        test_cp_validator.nova_client = Mock()
        test_cp_validator.nova_client.Client = Mock(return_value=mock_nova_client)

        self.cp_validator.validate_controller_url = Mock(return_value=True)
        self.cp_validator.validate_openstack_project = Mock(return_value=True)
        self.cp_validator.validate_openstack_domain = Mock(return_value=True)
        self.cp_validator.validate_openstack_username = Mock(return_value=True)
        self.cp_validator.validate_openstack_password = Mock(return_value=True)
        result = self.cp_validator.validate_openstack_credentials(openstack_session=mock_openstack_sesion,
                                                                  cs_session=mock_cs_session,
                                                                  cp_resource_model=mock_cp_resource_model,
                                                                  logger=self.mock_logger)
        self.assertTrue(result)

    def test_validate_all(self):
        mock_openstack_sesion = Mock()
        mock_cs_session = Mock()
        mock_cp_resource_model = Mock()

        self.cp_validator.validate_openstack_credentials = Mock(return_value=True)
        self.cp_validator.validate_region = Mock(return_value=True)
        self.cp_validator.validate_network_attributes = Mock(return_value=True)

        result = self.cp_validator.validate_all(openstack_session=mock_openstack_sesion,
                                                cs_session=mock_cs_session,
                                                cp_resource_model=mock_cp_resource_model,
                                                logger=self.mock_logger)

        self.cp_validator.validate_openstack_credentials.assert_called_with(openstack_session=mock_openstack_sesion,
                                                                            cs_session=mock_cs_session,
                                                                            cp_resource_model=mock_cp_resource_model,
                                                                            logger=self.mock_logger)

        self.cp_validator.validate_network_attributes.assert_called_with(openstack_session=mock_openstack_sesion,
                                                                         cp_resource_model=mock_cp_resource_model,
                                                                         logger=self.mock_logger)

    def test_validate_openstack_domain(self):
        test_os_domain = 'test'
        result = self.cp_validator.validate_openstack_domain(test_os_domain, self.mock_logger)
        self.assertTrue(result)

    def test_validate_openstack_project(self):
        test_os_project = 'test'
        result = self.cp_validator.validate_openstack_project(test_os_project, self.mock_logger)
        self.assertTrue(result)

    def test_validate_openstack_username(self):
        test_os_username = 'test'
        result = self.cp_validator.validate_openstack_username(test_os_username, self.mock_logger)
        self.assertTrue(result)

    def test_validate_openstack_password(self):
        test_os_password = 'test'
        result = self.cp_validator.validate_openstack_password(test_os_password, self.mock_logger)
        self.assertTrue(result)

    def test_mgmt_network_not_found(self):
        test_net_client = Mock()

        net_list = {'networks': []}
        test_net_client.list_networks = Mock(return_value=net_list)

        test_mgmt_network_id = 'test_mgmt_net'
        with self.assertRaises(ValueError) as context:
            result = self.cp_validator.validate_mgmt_network(net_client=test_net_client,
                                                             mgmt_network_id=test_mgmt_network_id,
                                                             logger=self.mock_logger)

        self.assertTrue(context)

    def test_mgmt_network_duplicate(self):
        test_net_client = Mock()

        net_list = {'networks': [{}, {}]}
        test_net_client.list_networks = Mock(return_value=net_list)

        test_mgmt_network_id = 'test_mgmt_net'
        with self.assertRaises(ValueError) as context:
            result = self.cp_validator.validate_mgmt_network(net_client=test_net_client,
                                                             mgmt_network_id=test_mgmt_network_id,
                                                             logger=self.mock_logger)

        self.assertTrue(context)

    def test_mgmt_network_empty(self):
        test_net_client = Mock()

        net_list = {'networks': []}
        test_net_client.list_networks = Mock(return_value=net_list)

        test_mgmt_network_id = ''
        with self.assertRaises(ValueError) as context:
            result = self.cp_validator.validate_mgmt_network(net_client=test_net_client,
                                                             mgmt_network_id=test_mgmt_network_id,
                                                             logger=self.mock_logger)

        self.assertTrue(context)

    def test_external_network_empty(self):
        test_net_client = Mock()

        net_list = {'networks': []}
        test_net_client.list_networks = Mock(return_value=net_list)

        test_floating_ip_subnet_id = ''
        with self.assertRaises(ValueError) as context:
            result = self.cp_validator.validate_floating_ip_subnet(net_client=test_net_client,
                                                                   floating_ip_subnet_id=test_floating_ip_subnet_id,
                                                                   logger=self.mock_logger)

        self.assertTrue(context)

    def test_external_network_not_external(self):
        test_net_client = Mock()

        mock_subnet_return_value = {'subnet': {'network_id': 'test_network_id'}}
        test_net_client.show_subnet = Mock(return_value=mock_subnet_return_value)

        net_list = {'networks': [{'router:external': False}]}
        test_net_client.list_networks = Mock(return_value=net_list)

        test_floating_ip_subnet_id = 'test_floating_ip_subnet_id'
        with self.assertRaises(ValueError) as context:
            result = self.cp_validator.validate_floating_ip_subnet(net_client=test_net_client,
                                                                   floating_ip_subnet_id=test_floating_ip_subnet_id,
                                                                   logger=self.mock_logger)

        self.assertTrue(context)

    def test_validate_reserved_networks(self):
        test_reserved_nets = '1.1.1.1/12,,2.2.2.2/16'

        test_cp_validator.ipaddress.ip_network = Mock()

        result = self.cp_validator.validate_reserved_networks(test_reserved_nets, self.mock_logger)

        self.assertTrue(result)

    def test_validate_openstack_credentials_raises_openstack_exception(self):
        mock_openstack_sesion = Mock()
        mock_cs_session = Mock()
        mock_cp_resource_model = Mock()
        mock_cp_resource_model.controller_url = "http://bla.com"

        mock_passwd = Mock()
        mock_passwd.Value = 'mock-passwd'
        mock_cs_session.DecryptPassword = Mock(return_value=mock_passwd)

        mock_nova_client = Mock()
        mock_nova_client.servers = Mock()
        mock_nova_client.servers.list = Mock(return_type=[])
        test_cp_validator.nova_client = Mock()
        test_cp_validator.nova_client.Client = Mock(
            side_effect=test_cp_validator.keystoneauth1.exceptions.http.NotFound)

        self.cp_validator.validate_controller_url = Mock(return_value=True)
        self.cp_validator.validate_openstack_domain = Mock(return_value=True)
        self.cp_validator.validate_openstack_project = Mock(return_value=True)
        self.cp_validator.validate_openstack_username = Mock(return_value=True)
        self.cp_validator.validate_openstack_password = Mock(return_value=True)

        with self.assertRaisesRegexp(ValueError, "Controller URL 'http://bla.com' is not found") as context:
            self.cp_validator.validate_openstack_credentials(openstack_session=mock_openstack_sesion,
                                                             cs_session=mock_cs_session,
                                                             cp_resource_model=mock_cp_resource_model,
                                                             logger=self.mock_logger)

        self.assertTrue(context)

        test_cp_validator.nova_client.Client = Mock(
            side_effect=test_cp_validator.keystoneauth1.exceptions.http.BadRequest)
        with self.assertRaises(test_cp_validator.keystoneauth1.exceptions.http.BadRequest) as context:
            self.cp_validator.validate_openstack_credentials(openstack_session=mock_openstack_sesion,
                                                             cs_session=mock_cs_session,
                                                             cp_resource_model=mock_cp_resource_model,
                                                             logger=self.mock_logger)

        self.assertTrue(context)

        test_cp_validator.nova_client.Client = Mock(
            side_effect=test_cp_validator.keystoneauth1.exceptions.http.Unauthorized)
        with self.assertRaises(test_cp_validator.keystoneauth1.exceptions.http.Unauthorized) as context:
            self.cp_validator.validate_openstack_credentials(openstack_session=mock_openstack_sesion,
                                                             cs_session=mock_cs_session,
                                                             cp_resource_model=mock_cp_resource_model,
                                                             logger=self.mock_logger)

        self.assertTrue(context)

    def test_validate_openstack_credentials_raises_unknown_exception(self):
        mock_openstack_sesion = Mock()
        mock_cs_session = Mock()
        mock_cp_resource_model = Mock()

        mock_passwd = Mock()
        mock_passwd.Value = 'mock-passwd'
        mock_cs_session.DecryptPassword = Mock(return_value=mock_passwd)

        mock_nova_client = Mock()
        mock_nova_client.servers = Mock()
        mock_nova_client.servers.list = Mock(return_type=[])
        test_cp_validator.nova_client = Mock()
        test_cp_validator.nova_client.Client = Mock(side_effect=Exception)

        self.cp_validator.validate_controller_url = Mock(return_value=True)
        self.cp_validator.validate_openstack_domain = Mock(return_value=True)
        self.cp_validator.validate_openstack_project = Mock(return_value=True)
        self.cp_validator.validate_openstack_username = Mock(return_value=True)
        self.cp_validator.validate_openstack_password = Mock(return_value=True)

        with self.assertRaises(Exception) as context:
            self.cp_validator.validate_openstack_credentials(openstack_session=mock_openstack_sesion,
                                                             cs_session=mock_cs_session,
                                                             cp_resource_model=mock_cp_resource_model,
                                                             logger=self.mock_logger)

        self.assertTrue(context)

    def test_validate_openstack_credentials_attrs_false(self):
        mock_openstack_sesion = Mock()
        mock_cs_session = Mock()
        mock_cp_resource_model = Mock()

        self.cp_validator.validate_controller_url = Mock(return_value=False)
        result = self.cp_validator.validate_openstack_credentials(openstack_session=mock_openstack_sesion,
                                                                  cs_session=mock_cs_session,
                                                                  cp_resource_model=mock_cp_resource_model,
                                                                  logger=self.mock_logger)
        self.assertFalse(result)

        self.cp_validator.validate_controller_url = Mock(return_value=True)
        self.cp_validator.validate_openstack_domain = Mock(return_value=False)
        result = self.cp_validator.validate_openstack_credentials(openstack_session=mock_openstack_sesion,
                                                                  cs_session=mock_cs_session,
                                                                  cp_resource_model=mock_cp_resource_model,
                                                                  logger=self.mock_logger)
        self.assertFalse(result)

        self.cp_validator.validate_controller_url = Mock(return_value=True)
        self.cp_validator.validate_openstack_domain = Mock(return_value=True)
        self.cp_validator.validate_openstack_project = Mock(return_value=False)
        result = self.cp_validator.validate_openstack_credentials(openstack_session=mock_openstack_sesion,
                                                                  cs_session=mock_cs_session,
                                                                  cp_resource_model=mock_cp_resource_model,
                                                                  logger=self.mock_logger)
        self.assertFalse(result)

        self.cp_validator.validate_controller_url = Mock(return_value=True)
        self.cp_validator.validate_openstack_project = Mock(return_value=True)
        self.cp_validator.validate_openstack_domain = Mock(return_value=True)
        self.cp_validator.validate_openstack_username = Mock(return_value=False)
        result = self.cp_validator.validate_openstack_credentials(openstack_session=mock_openstack_sesion,
                                                                  cs_session=mock_cs_session,
                                                                  cp_resource_model=mock_cp_resource_model,
                                                                  logger=self.mock_logger)
        self.assertFalse(result)

        self.cp_validator.validate_controller_url = Mock(return_value=True)
        self.cp_validator.validate_openstack_project = Mock(return_value=True)
        self.cp_validator.validate_openstack_domain = Mock(return_value=True)
        self.cp_validator.validate_openstack_username = Mock(return_value=True)
        self.cp_validator.validate_openstack_password = Mock(return_value=False)
        result = self.cp_validator.validate_openstack_credentials(openstack_session=mock_openstack_sesion,
                                                                  cs_session=mock_cs_session,
                                                                  cp_resource_model=mock_cp_resource_model,
                                                                  logger=self.mock_logger)
        self.assertFalse(result)
