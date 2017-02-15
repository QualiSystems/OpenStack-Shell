from unittest import TestCase

import mock

from cloudshell.cp.openstack.common.deploy_data_holder import DeployDataHolder


class TestDeployDataHolder(TestCase):

    def setUp(self):
        super(TestDeployDataHolder, self).setUp()
        self.tested_class = DeployDataHolder

    def test_create_from_params(self):
        """Check that method will create and return instance with given params"""
        test_template_model = mock.Mock()
        test_datastore_name = mock.Mock()
        test_vm_cluster_model = mock.Mock()
        test_ip_regex = mock.Mock()
        test_refresh_ip_timeout = mock.Mock()
        test_auto_power_on = mock.Mock()
        test_auto_power_off = mock.Mock()
        test_wait_for_ip = mock.Mock()
        test_auto_delete = mock.Mock()

        instance = self.tested_class.create_from_params(
            template_model=test_template_model,
            datastore_name=test_datastore_name,
            vm_cluster_model=test_vm_cluster_model,
            ip_regex=test_ip_regex,
            refresh_ip_timeout=test_refresh_ip_timeout,
            auto_power_on=test_auto_power_on,
            auto_power_off=test_auto_power_off,
            wait_for_ip=test_wait_for_ip,
            auto_delete=test_auto_delete)

        self.assertEqual(instance.template_model, test_template_model)
        self.assertEqual(instance.datastore_name, test_datastore_name)
        self.assertEqual(instance.vm_cluster_model, test_vm_cluster_model)
        self.assertEqual(instance.ip_regex, test_ip_regex)
        self.assertEqual(instance.refresh_ip_timeout, test_refresh_ip_timeout)
        self.assertEqual(instance.auto_power_on, test_auto_power_on)
        self.assertEqual(instance.auto_power_off, test_auto_power_off)
        self.assertEqual(instance.wait_for_ip, test_wait_for_ip)
        self.assertEqual(instance.auto_delete, test_auto_delete)

    def test_is_primitive_returns_true(self):
        """Check that method will return True for all primitive types"""
        for primitive_type in (535, "test_string", False, 12.45, u"test_unicode_stirng"):
            is_primitive = self.tested_class._is_primitive(primitive_type)
            self.assertTrue(is_primitive)

    def test_is_primitive_returns_false(self):
        """Check that method will return False for non-primitive types"""
        class TestClass:
            pass

        for primitive_type in (TestClass(), [], {}):
            is_primitive = self.tested_class._is_primitive(primitive_type)
            self.assertFalse(is_primitive)

    def test_create_obj_by_type(self):
        """Check that method will return the same object if object is not list, dict or some primitive type"""
        test_obj = mock.MagicMock()
        returned_obj = self.tested_class._create_obj_by_type(test_obj)
        self.assertIs(returned_obj, test_obj)

    def test_create_obj_by_type_from_dict(self):
        """Check that method will return DeployDataHolder instance for the dict object"""
        test_obj = {}
        returned_obj = self.tested_class._create_obj_by_type(test_obj)
        self.assertIsInstance(returned_obj, self.tested_class)

    def test_create_obj_by_type_from_list(self):
        """Check that method will return list with converted instances for the list object"""
        test_obj = [mock.MagicMock(), "test_atrt", {}]
        returned_obj = self.tested_class._create_obj_by_type(test_obj)
        self.assertIsInstance(returned_obj, list)
        self.assertIs(returned_obj[0], test_obj[0])
        self.assertEqual(returned_obj[1], test_obj[1])
        self.assertIsInstance(returned_obj[2], self.tested_class)

    def test_create_obj_by_type_from_primitive_type(self):
        """Check that method will return same primitive for the primitive object"""
        test_obj = "test_primitive"
        returned_obj = self.tested_class._create_obj_by_type(test_obj)
        self.assertEqual(returned_obj, test_obj)
