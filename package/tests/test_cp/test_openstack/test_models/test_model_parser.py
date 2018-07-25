from unittest import TestCase

import mock
from cloudshell.cp.openstack.models.deploy_os_nova_image_instance_deployment_model import \
    DeployOSNovaImageInstanceDeploymentModel

from cloudshell.cp.openstack.models.model_parser import OpenStackShellModelParser


class TestOpenStackShellModelParser(TestCase):
    def setUp(self):
        super(TestOpenStackShellModelParser, self)
        self.tested_class = OpenStackShellModelParser

    def test_get_resource_model_from_context(self):
        test_resource = mock.Mock()
        test_resource.attributes = {'Controller URL': 'test url', 'OpenStack Domain Name': 'test_domain',
                                    'OpenStack Project Name': 'test_project', 'User Name': 'test_user',
                                    'Password': 'test_pass', 'OpenStack Management Network ID': '1234-56-78',
                                    'Floating IP Pool': '10.0.0.100-10.0.0.101',
                                    'OpenStack Reserved Networks': '172.22.0.0/16', 'Vlan Type': 'vlan',
                                    'OpenStack Physical Interface Name': 'public',
                                    'Floating IP Subnet ID': 'floating_ip_subnet_id'}
        result = self.tested_class.get_resource_model_from_context(test_resource)

        self.assertEqual(result.controller_url, 'test url')
        self.assertEqual(result.os_domain_name, 'test_domain')
        self.assertEqual(result.os_project_name, 'test_project')
        self.assertEqual(result.os_user_name, 'test_user')
        self.assertEqual(result.os_user_password, 'test_pass')
        self.assertEqual(result.qs_mgmt_os_net_uuid, '1234-56-78')
        self.assertEqual(result.reserved_networks, '172.22.0.0/16')
        self.assertEqual(result.vlan_type, 'vlan')
        self.assertEqual(result.provider_network_interface, 'public')
        self.assertEqual(result.floating_ip_subnet_uuid, 'floating_ip_subnet_id')

    @mock.patch("cloudshell.cp.openstack.models.model_parser.jsonpickle")
    def test_deploy_res_model_appname_from_deploy_req(self, jsonpickle):
        """Check that method returns DeployOSNovaImageInstanceDeploymentModel instance with attrs from DeployDataHolder"""
        test_deploy_req = mock.MagicMock()
        attr = mock.MagicMock()
        data = {'Attributes': attr, 'AppName': 'app_name'}
        jsonpickle.decode.return_value = data
        deploy_res_model, app_name = self.tested_class.deploy_res_model_appname_from_deploy_req(test_deploy_req)

        self.assertEqual(app_name, data['AppName'])
        self.assertTrue(deploy_res_model, isinstance(deploy_res_model, DeployOSNovaImageInstanceDeploymentModel))
        self.assertEqual(deploy_res_model.cloud_provider, None)
        self.assertEqual(deploy_res_model.availability_zone, attr['Availability Zone'])
        self.assertEqual(deploy_res_model.image_id, attr['Image ID'])
        self.assertEqual(deploy_res_model.instance_flavor, attr['Instance Flavor'])
        self.assertEqual(deploy_res_model.add_floating_ip,
                         OpenStackShellModelParser.parse_boolean(attr['Add Floating IP']))
        self.assertEqual(deploy_res_model.autoload, OpenStackShellModelParser.parse_boolean(attr['Autoload']))
        self.assertEqual(deploy_res_model.affinity_group_id, attr['Affinity Group ID'])
        self.assertEqual(deploy_res_model.floating_ip_subnet_id, attr['Floating IP Subnet ID'])
        self.assertEqual(deploy_res_model.autoload, OpenStackShellModelParser.parse_boolean(attr['Auto udev']))

    def test_parse_boolean_return_true(self):
        """Check that method correctly parses True values"""
        for test_value in ('1', 'True'):
            result = self.tested_class.parse_boolean(test_value)
            self.assertTrue(result)

    def test_parse_boolean_return_false(self):
        """Check that method correctly parses False values"""
        for test_value in ('0', 'False'):
            result = self.tested_class.parse_boolean(test_value)
            self.assertFalse(result)

    @mock.patch("cloudshell.cp.openstack.models.model_parser.jsonpickle")
    @mock.patch("cloudshell.cp.openstack.models.model_parser.DeployDataHolder")
    def test_deployed_app_resource_from_context_remote(self, deploy_data_holder_class, jsonpickle):
        """Check that method returns DeployDataHolder instance"""
        test_context_remote = mock.MagicMock()
        deploy_data_holder = mock.MagicMock()
        deploy_data_holder_class.return_value = deploy_data_holder

        result = self.tested_class.deployed_app_resource_from_context_remote(test_context_remote)

        self.assertIs(result, deploy_data_holder)

    # @mock.patch("cloudshell.cp.openstack.models.model_parser.OpenStackShellModelParser")
    @mock.patch("cloudshell.cp.openstack.models.model_parser.DeployOSNovaImageInstanceDeploymentModel")
    def test_get_deploy_resource_model_from_context_resource(self, deploy_os_nova_image_instance_resource_model_class):
        """Check that method returns DeployOSNovaImageInstanceDeploymentModel instance with correct attributes"""
        deploy_os_nova_image_instance_resource_model = mock.MagicMock()
        parse_boolean_result = mock.MagicMock()
        deploy_os_nova_image_instance_resource_model_class.return_value = deploy_os_nova_image_instance_resource_model
        test_resource = mock.MagicMock()
        test_resource.attributes = {}
        test_resource.attributes['Cloud Provider'] = test_cloud_provider = 'test_cloud_provider'
        test_resource.attributes['Availability Zone'] = test_availability_zone = 'test_availability_zone'
        test_resource.attributes['Image ID'] = test_image_uuid = 'test_image_uuid'
        test_resource.attributes['Instance Flavor'] = test_instance_flavor = 'test_instance_flavor'
        test_resource.attributes['Add Floating IP'] = 'True'
        test_resource.attributes['Autoload'] = '1'
        test_resource.attributes['Floating IP Subnet ID'] = floating_ip_subnet_uuid = 'floating_ip_subnet_id'
        test_resource.attributes['Affinity Group ID'] = affinity_group_uuid = 'affinity_group_id'
        test_resource.attributes['Auto udev'] = 'True'

        deploy_resource_model = self.tested_class.get_deploy_resource_model_from_context_resource(test_resource)

        self.assertEqual(deploy_resource_model.cloud_provider, test_cloud_provider)
        self.assertEqual(deploy_resource_model.availability_zone, test_availability_zone)
        self.assertEqual(deploy_resource_model.image_id, test_image_uuid)
        self.assertEqual(deploy_resource_model.instance_flavor, test_instance_flavor)
        self.assertEqual(deploy_resource_model.add_floating_ip, True)
        self.assertEqual(deploy_resource_model.autoload, True)
        self.assertEqual(deploy_resource_model.floating_ip_subnet_id, floating_ip_subnet_uuid)
        self.assertEqual(deploy_resource_model.affinity_group_id, affinity_group_uuid)

    # @mock.patch("cloudshell.cp.openstack.models.model_parser.OpenStackShellModelParser")
    @mock.patch("cloudshell.cp.openstack.models.model_parser.DeployOSNovaImageInstanceDeploymentModel")
    def test_get_deploy_resource_model_from_context_resource_without_cloud_provider_attribute(self,
                                                                                              deploy_os_nova_image_instance_resource_model_class):
        """Check that method returns DeployOSNovaImageInstanceDeploymentModel instance with correct attributes"""
        deploy_os_nova_image_instance_resource_model = mock.MagicMock()
        parse_boolean_result = mock.MagicMock()
        deploy_os_nova_image_instance_resource_model_class.return_value = deploy_os_nova_image_instance_resource_model
        # openstack_shell_model_parser_class.parse_boolean.return_value = parse_boolean_result
        test_resource = mock.MagicMock()
        test_resource.attributes = {}
        test_resource.attributes['Availability Zone'] = test_availability_zone = 'test_availability_zone'
        test_resource.attributes['Image ID'] = test_image_uuid = 'test_image_uuid'
        test_resource.attributes['Instance Flavor'] = test_instance_flavor = 'test_instance_flavor'
        test_resource.attributes['Add Floating IP'] = 'True'
        test_resource.attributes['Autoload'] = '1'
        test_resource.attributes['Floating IP Subnet ID'] = floating_ip_subnet_uuid = 'floating_ip_subnet_id'
        test_resource.attributes['Affinity Group ID'] = affinity_group_uuid = 'affinity_group_id'
        test_resource.attributes['Auto udev'] = 'True'

        deploy_resource_model = self.tested_class.get_deploy_resource_model_from_context_resource(test_resource)

        self.assertEqual(deploy_resource_model.availability_zone, test_availability_zone)
        self.assertEqual(deploy_resource_model.image_id, test_image_uuid)
        self.assertEqual(deploy_resource_model.instance_flavor, test_instance_flavor)
        self.assertEqual(deploy_resource_model.add_floating_ip, True)
        self.assertEqual(deploy_resource_model.autoload, True)
        self.assertEqual(deploy_resource_model.floating_ip_subnet_id, floating_ip_subnet_uuid)
        self.assertEqual(deploy_resource_model.affinity_group_id, affinity_group_uuid)
        self.assertEqual(deploy_resource_model.auto_udev, True)

    def test_get_attribute_value_by_name_ignoring_namespace_with_namespace(self):
        # Arrange
        attr_name = "attr1"
        attr_dict = {"attr2": "val2", "ns1.ns2.attr1": "val1"}

        # Act
        val = self.tested_class.get_attribute_value_by_name_ignoring_namespace(attr_dict, attr_name)

        # Assert
        self.assertEquals(val, "val1")

    def test_get_attribute_value_by_name_ignoring_namespace_with_namespace_2(self):
        # Arrange
        attr_name = "attr1"
        attr_dict = {"attr2": "val2", "attr1": "val1"}

        # Act
        val = self.tested_class.get_attribute_value_by_name_ignoring_namespace(attr_dict, attr_name)

        # Assert
        self.assertEquals(val, "val1")




