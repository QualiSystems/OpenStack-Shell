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
        test_resource.attributes['Quali Management Network UUID'] = '1234-56'
        test_resource.attributes['Floating IP Pool']  = '10.0.0.100-10.0.0.101'

        result = self.os_shell_model_parser.get_resource_model_from_context(test_resource)
        self.assertEqual(result.controller_url, 'test url')
        self.assertEqual(result.os_domain_name, 'test_domain')
        self.assertEqual(result.os_project_name, 'test_project')
        self.assertEqual(result.os_region, 'test_region')
        self.assertEqual(result.os_user_name, 'test_user')
        self.assertEqual(result.os_user_password, 'test_pass')
        self.assertEqual(result.qs_mgmt_os_net_uuid, '1234-56')
        self.assertEqual(result.os_floating_ip_pool, '10.0.0.100-10.0.0.101')