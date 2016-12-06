from unittest import TestCase

import mock

from cloudshell.cp.openstack.models.model_parser import OpenStackShellModelParser


class TestOpenStackShellModelParser(TestCase):
    def setUp(self):
        super(TestOpenStackShellModelParser, self)
        self.tested_class = OpenStackShellModelParser

    def test_get_resource_model_from_context(self):
        test_resource = mock.Mock()
        test_resource.attributes = {}
        test_resource.attributes['Controller URL'] = 'test url'
        test_resource.attributes['OpenStack Domain Name'] = 'test_domain'
        test_resource.attributes['OpenStack Project Name'] = 'test_project'
        test_resource.attributes['OpenStack Region'] = 'test_region'
        test_resource.attributes['OpenStack User Name']  = 'test_user'
        test_resource.attributes['OpenStack User Password'] = 'test_pass'
        test_resource.attributes['Quali Management Network UUID'] = '1234-56-78'
        test_resource.attributes['Floating IP Pool']  = '10.0.0.100-10.0.0.101'
        test_resource.attributes['Reserved Networks'] = '172.22.0.0/16'
        test_resource.attributes['Provider Network Type'] = 'vlan'
        test_resource.attributes['Provider Network Interface'] = 'public'

        result = self.tested_class.get_resource_model_from_context(test_resource)

        self.assertEqual(result.controller_url, 'test url')
        self.assertEqual(result.os_domain_name, 'test_domain')
        self.assertEqual(result.os_project_name, 'test_project')
        self.assertEqual(result.os_region, 'test_region')
        self.assertEqual(result.os_user_name, 'test_user')
        self.assertEqual(result.os_user_password, 'test_pass')
        self.assertEqual(result.qs_mgmt_os_net_uuid, '1234-56-78')
        self.assertEqual(result.os_floating_ip_pool, '10.0.0.100-10.0.0.101')
        self.assertEqual(result.reserved_networks, '172.22.0.0/16')
        self.assertEqual(result.provider_network_type, 'vlan')
        self.assertEqual(result.provider_network_interface, 'public')

    @mock.patch("cloudshell.cp.openstack.models.model_parser.jsonpickle")
    @mock.patch("cloudshell.cp.openstack.models.model_parser.DeployOSNovaImageInstanceResourceModel")
    @mock.patch("cloudshell.cp.openstack.models.model_parser.DeployDataHolder")
    def test_deploy_res_model_appname_from_deploy_req(self, deploy_data_holder_class,
                                                      deploy_os_nova_image_instance_resource_model_class,
                                                      jsonpickle):
        """Check that method returns DeployOSNovaImageInstanceResourceModel instance with attrs from DeployDataHolder"""
        test_deploy_req = mock.MagicMock()
        deploy_data_holder = mock.MagicMock()
        deploy_os_nova_image_instance_resource_model = mock.MagicMock()
        deploy_data_holder_class.return_value = deploy_data_holder
        deploy_os_nova_image_instance_resource_model_class.return_value = deploy_os_nova_image_instance_resource_model

        deploy_res_model, app_name = self.tested_class.deploy_res_model_appname_from_deploy_req(test_deploy_req)

        self.assertEqual(app_name, deploy_data_holder.app_name)
        self.assertIs(deploy_res_model, deploy_os_nova_image_instance_resource_model)
        self.assertEqual(deploy_res_model.cloud_provider, deploy_data_holder.image.cloud_provider)
        self.assertEqual(deploy_res_model.cp_avail_zone, deploy_data_holder.image.cp_avail_zone)
        self.assertEqual(deploy_res_model.img_uuid, deploy_data_holder.image.img_uuid)
        self.assertEqual(deploy_res_model.instance_flavor, deploy_data_holder.image.instance_flavor)
        self.assertEqual(deploy_res_model.add_floating_ip, deploy_data_holder.image.add_floating_ip)
        self.assertEqual(deploy_res_model.autoload, deploy_data_holder.image.autoload)
        self.assertEqual(deploy_res_model.inbound_ports, deploy_data_holder.image.inbound_ports)
        self.assertEqual(deploy_res_model.outbound_ports, deploy_data_holder.image.outbound_ports)

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

    @mock.patch("cloudshell.cp.openstack.models.model_parser.OpenStackShellModelParser")
    @mock.patch("cloudshell.cp.openstack.models.model_parser.DeployOSNovaImageInstanceResourceModel")
    def test_get_deploy_resource_model_from_context_resource(self, deploy_os_nova_image_instance_resource_model_class,
                                                             openstack_shell_model_parser_class):
        """Check that method returns DeployOSNovaImageInstanceResourceModel instance with correct attributes"""
        deploy_os_nova_image_instance_resource_model = mock.MagicMock()
        parse_boolean_result = mock.MagicMock()
        deploy_os_nova_image_instance_resource_model_class.return_value = deploy_os_nova_image_instance_resource_model
        openstack_shell_model_parser_class.parse_boolean.return_value = parse_boolean_result
        test_resource = mock.MagicMock()
        test_resource.attributes = {}
        test_resource.attributes['Cloud Provider'] = test_cloud_provider = 'test_cloud_provider'
        test_resource.attributes['Availability Zone'] = test_availability_zone = 'test_availability_zone'
        test_resource.attributes['Image UUID'] = test_image_uuid = 'test_image_uuid'
        test_resource.attributes['Instance Flavor'] = test_instance_flavor = 'test_instance_flavor'
        test_resource.attributes['Add Floating IP'] = 'True'
        test_resource.attributes['Autoload'] = '1'
        test_resource.attributes['Inbound Ports'] = inbound_ports = 'test_inbound_ports'
        test_resource.attributes['Outbound Ports'] = outbounds_ports = 'test_outbound_ports'

        deploy_resource_model = self.tested_class.get_deploy_resource_model_from_context_resource(test_resource)

        self.assertIs(deploy_resource_model, deploy_os_nova_image_instance_resource_model)
        self.assertEqual(deploy_resource_model.cloud_provider, test_cloud_provider)
        self.assertEqual(deploy_resource_model.cp_avail_zone, test_availability_zone)
        self.assertEqual(deploy_resource_model.img_uuid, test_image_uuid)
        self.assertEqual(deploy_resource_model.instance_flavor, test_instance_flavor)
        self.assertEqual(deploy_resource_model.add_floating_ip, parse_boolean_result)
        self.assertEqual(deploy_resource_model.autoload, parse_boolean_result)
        self.assertEqual(deploy_resource_model.inbound_ports, inbound_ports)
        self.assertEqual(deploy_resource_model.outbound_ports, outbounds_ports)
