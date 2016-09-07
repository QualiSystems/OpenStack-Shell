from unittest import TestCase
from mock import Mock

from cloudshell.cp.openstack.models.model_parser import OpenStackShellModelParser


class TestOpenStackShellModelParser(TestCase):
    def setUp(self):
        self.os_shell_model_parser = OpenStackShellModelParser()

    def test_get_resource_model_from_context(self):

        test_resource = Mock()
        test_resource.attributes = {}
        test_resource.attributes['Controller URL'] = 'test url'
        test_resource.attributes['OpenStack Domain Name'] = 'test_domain'
        test_resource.attributes['OpenStack Project Name'] = 'test_project'
        test_resource.attributes['OpenStack Region'] = 'test_region'
        test_resource.attributes['OpenStack User Name']  = 'test_user'
        test_resource.attributes['OpenStack User Password'] = 'test_pass'
        test_resource.attributes['OpenStack Management VLAN ID'] = 123
        test_resource.attributes['Quali Management VLAN ID'] = 234
        test_resource.attributes['OpenStack Management Subnet CIDR'] = '10.0.0.0/8'
        test_resource.attributes['Quali Management Subnet CIDR'] = '10.0.0.0/16'
        test_resource.attributes['Floating IP Pool']  = '10.0.0.100-10.0.0.101'

        result = self.os_shell_model_parser.get_resource_model_from_context(test_resource)
        self.assertEqual(result.controller_url, 'test url')
        self.assertEqual(result.os_domain_name, 'test_domain')
        self.assertEqual(result.os_project_name, 'test_project')
        self.assertEqual(result.os_region, 'test_region')
        self.assertEqual(result.os_user_name, 'test_user')
        self.assertEqual(result.os_user_password, 'test_pass')
        self.assertEqual(result.os_mgmt_vlan_id, 123)
        self.assertEqual(result.qs_mgmt_vlan_id, 234)
        self.assertEqual(result.os_mgmt_subnet_cidr, '10.0.0.0/8')
        self.assertEqual(result.qs_mgmt_subnet_cidr, '10.0.0.0/16')
        self.assertEqual(result.os_floating_ip_pool, '10.0.0.100-10.0.0.101')