from unittest import TestCase
from mock import Mock

import cloudshell.cp.openstack.domain.services.cp_validators.cp_validator as test_cp_validator
from cloudshell.cp.openstack.models.openstack_resource_model import OpenStackResourceModel
from cloudshell.cp.openstack.domain.services.cp_validators.cp_validator import OpenStackCPValidator
class TestOpenStackSessionProvider(TestCase):
    def setUp(self):
        mock_context = Mock()
        mock_context.resource = Mock()
        mock_context.resource.name = 'test_resource'

        test_cp_resource = OpenStackResourceModel()
        mock_model_parser = Mock()
        mock_model_parser.get_resource_model_from_context = Mock(return_value=test_cp_resource)
        test_cp_validator.OpenStackShellModelParser = Mock(return_value=mock_model_parser)

        test_cp_validator.get_qs_logger = Mock(return_value=Mock())

        mock_cs_helper = Mock()
        test_cp_validator.CloudshellDriverHelper = Mock(return_value=mock_cs_helper)
        mock_cs_helper.get_session = Mock(return_value=Mock())

        mock_session = Mock()
        test_cp_validator.OpenStackSessionProvider = Mock(return_value=mock_session)
        mock_session.get_openstack_session = Mock(return_value=Mock())

        self.cp_validator = OpenStackCPValidator(mock_context)

    def test_validate_controller_url_empty_url(self):

        test_empty_url = ''
        with self.assertRaises(ValueError) as context:
            self.cp_validator.validate_controller_url(test_empty_url)

        self.assertTrue(context)

    def test_validate_empty_url_not_start_with_http(self):

        test_nohttp_url = 'test'

        with self.assertRaises(ValueError) as context:
            self.cp_validator.validate_controller_url(test_nohttp_url)

        self.assertTrue(context)

    def test_valid_controller_url(self):

        valid_url = 'http://example.com:5000'

        self.assertTrue(self.cp_validator.validate_controller_url(valid_url))


    def test_invalid_vlan_type(self):
        test_net_client = Mock()
        test_vlan_type = 'test'
        test_provider_net_interface = 'test_interface'

        with self.assertRaises(ValueError) as context:
            self.cp_validator.validate_vlan_type(net_client=test_net_client,
                                             vlan_type=test_vlan_type,
                                             provider_net_interface=test_provider_net_interface)
        self.assertTrue(context)


    def test_validate_vlan_type_success(self):

        test_net_client = Mock()

        test_net_client.create_network = Mock(return_value={'network': {'id':'test_id'}})
        test_net_client.delete_network = Mock()

        test_vlan_type = 'vlan'
        test_provider_net_interface = 'test_interface'

        result = self.cp_validator.validate_vlan_type(net_client=test_net_client,
                                             vlan_type=test_vlan_type,
                                             provider_net_interface=test_provider_net_interface)

        self.assertTrue(result)


    def test_validate_external_network(self):

        test_net_client = Mock()

        net_list = {'networks': [{'router:external': True}]}
        test_net_client.list_networks = Mock(return_value=net_list)

        test_external_network_id = 'test_external_net'

        result = self.cp_validator.validate_external_network(net_client=test_net_client,
                                                             external_network_id=test_external_network_id)

        self.assertTrue(result)