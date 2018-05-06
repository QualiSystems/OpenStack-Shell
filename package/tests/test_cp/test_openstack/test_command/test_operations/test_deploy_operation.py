from unittest import TestCase
from mock import Mock

from cloudshell.cp.openstack.command.operations.deploy_operation import DeployOperation
from cloudshell.cp.openstack.models.deploy_result_model import DeployResultModel

import json
from cloudshell.cp.core.models import *

class TestDeployOperation(TestCase):
    def setUp(self):
        self.cancellation_service = Mock()
        self.instance_service = Mock()
        self.network_service = Mock()
        self.vm_details_provider = Mock()
        self.deploy_operation = DeployOperation(cancellation_service=self.cancellation_service,
                                                instance_service=self.instance_service,
                                                network_service=self.instance_service,
                                                vm_details_provider=self.vm_details_provider)
        self.deploy_operation.instance_service = Mock()
        self.deploy_operation.instance_waiter = Mock()

        self.openstack_session = Mock()
        self.reservation = Mock()
        self.mock_logger = Mock()
        self.cp_resource_model = Mock()

    def test_deploy_instance_success(self):
        test_name = 'test name'
        test_id = '1234'
        test_cloud_provider = 'test CP'
        test_private_ip = '1.2.3.4'
        test_floating_ip = '4.3.2.1'
        test_deployed_app_attrs = {'Public IP': 'test_public_ip'}
        mock_deploy_result = DeployResultModel(vm_name=test_name,
                                               vm_uuid=test_id,
                                               deployed_app_ip=test_private_ip,
                                               deployed_app_attributes=test_deployed_app_attrs,
                                               floating_ip=test_floating_ip,
                                               vm_details_data='')

        self.deploy_operation.instance_service.get_private_ip = Mock(return_value=test_private_ip)

        test_instance = Mock()
        test_instance.name = test_name
        test_instance.id = test_id

        self.deploy_operation.instance_service.create_instance = Mock(return_value=test_instance)

        mock_floating_ip_str = '1.2.3.4'
        mock_floating_ip_dict = {'floating_ip_address': mock_floating_ip_str}
        self.deploy_operation.network_service.create_floating_ip = Mock(return_value=mock_floating_ip_dict)

        test_deploy_req_model = Mock()
        test_deploy_req_model.cloud_provider = test_cloud_provider

        mock_cancellation_context = Mock()

        test_result = self.deploy_operation.deploy(os_session=self.openstack_session,
                                                   reservation=self.reservation,
                                                   cp_resource_model=self.cp_resource_model,
                                                   deploy_app_action=test_deploy_req_model,
                                                   cancellation_context=mock_cancellation_context,
                                                   logger=self.mock_logger)

        self.assertEqual(test_result.vm_name, test_name)
        self.assertEqual(test_result.vm_uuid, test_id)
        self.assertEqual(test_result.deployed_app_address, test_private_ip)

    def test_deploy_instance_success_new(self):
        test_name = 'test name'
        test_id = '1234'
        test_cloud_provider = 'test CP'
        test_private_ip = '1.2.3.4'
        test_floating_ip = '4.3.2.1'
        test_deployed_app_attrs = {'Public IP': 'test_public_ip'}
        mock_deploy_result = DeployResultModel(vm_name=test_name,
                                               vm_uuid=test_id,
                                               deployed_app_ip=test_private_ip,
                                               deployed_app_attributes=test_deployed_app_attrs,
                                               floating_ip=test_floating_ip,
                                               vm_details_data='')

        self.deploy_operation.instance_service.get_private_ip = Mock(return_value=test_private_ip)

        test_instance = Mock()
        test_instance.name = test_name
        test_instance.id = test_id

        self.deploy_operation.instance_service.create_instance = Mock(return_value=test_instance)

        mock_floating_ip_str = '1.2.3.4'
        mock_floating_ip_dict = {'floating_ip_address': mock_floating_ip_str}
        self.deploy_operation.network_service.create_floating_ip = Mock(return_value=mock_floating_ip_dict)

        test_deploy_req_model = Mock()
        test_deploy_req_model.cloud_provider = test_cloud_provider

        mock_cancellation_context = Mock()

        test_result = self.deploy_operation.deploy(os_session=self.openstack_session,
                                                   reservation=self.reservation,
                                                   cp_resource_model=self.cp_resource_model,
                                                   deploy_app_action=test_deploy_req_model,
                                                   cancellation_context=mock_cancellation_context,
                                                   logger=self.mock_logger)

        self.assertEqual(test_result.vm_name, test_name)
        self.assertEqual(test_result.vm_uuid, test_id)
        self.assertEqual(test_result.deployed_app_address, test_private_ip)
    def test_deploy_instance_create_instance_none(self):
        self.deploy_operation.instance_service.create_instance = Mock(return_value=None)

        test_name = 'test'
        test_deploy_req_model = Mock()
        mock_cancellation_context = Mock()
        result = self.deploy_operation.deploy(os_session=self.openstack_session,
                                         reservation=self.reservation,
                                         cp_resource_model=self.cp_resource_model,
                                         deploy_app_action=test_deploy_req_model,
                                         cancellation_context=mock_cancellation_context,
                                         logger=self.mock_logger)

        self.assertIsInstance(result,DeployAppResult)

        self.assertEqual(result.errorMessage ,"Create Instance Returned None")
        print json.dumps(result, default=lambda o: o.__dict__, sort_keys=True, indent=4)



    def test_deploy_instance_no_mgmt_network_ip(self):
        test_name = 'test name'
        test_id = '1234'
        test_cloud_provider = 'test CP'
        test_floating_ip = '4.3.2.1'
        test_deployed_app_attrs = {'Public IP': 'test_public_ip'}

        self.deploy_operation.instance_service.get_instance_mgmt_network_name = Mock(return_value=None)

        test_instance = Mock()
        test_instance.name = test_name
        test_instance.id = test_id

        self.deploy_operation.instance_service.create_instance = Mock(return_value=test_instance)

        mock_floating_ip_str = '1.2.3.4'
        mock_floating_ip_dict = {'floating_ip_address': mock_floating_ip_str}
        self.deploy_operation.network_service.create_floating_ip = Mock(return_value=mock_floating_ip_dict)

        test_deploy_req_model = Mock()
        test_deploy_req_model.cloud_provider = test_cloud_provider
        test_deploy_req_model.floating_ip_subnet_uuid = ''

        mock_cancellation_context = Mock()

        self.deploy_operation.instance_service.detach_floating_ip = Mock()
        self.deploy_operation.network_service.delete_floating_ip = Mock()
        self.deploy_operation.instance_service.terminate_instance = Mock()

        with self.assertRaises(ValueError) as context:
            self.deploy_operation.deploy(os_session=self.openstack_session,
                                         reservation=self.reservation,
                                         cp_resource_model=self.cp_resource_model,
                                         deploy_app_action=test_deploy_req_model,
                                         cancellation_context=mock_cancellation_context,
                                         logger=self.mock_logger)

        self.deploy_operation.instance_service.detach_floating_ip.assert_called_with(
            openstack_session=self.openstack_session,
            instance=test_instance,
            floating_ip='',
            logger=self.mock_logger)
        self.deploy_operation.instance_service.terminate_instance.assert_called_with(
            openstack_session=self.openstack_session,
            instance_id=test_id,
            logger=self.mock_logger)
        self.deploy_operation.network_service.delete_floating_ip.assert_called_with(
            openstack_session=self.openstack_session,
            floating_ip='',
            logger=self.mock_logger)
        self.assertTrue(context)

    def test_deploy_instance_no_floating_ip(self):
        test_name = 'test name'
        test_id = '1234'
        test_cloud_provider = 'test CP'
        test_floating_ip = '4.3.2.1'
        test_deployed_app_attrs = {'Public IP': 'test_public_ip'}

        self.deploy_operation.instance_service.get_instance_mgmt_network_name = Mock(return_value=test_name)

        test_instance = Mock()
        test_instance.name = test_name
        test_instance.id = test_id

        self.deploy_operation.instance_service.create_instance = Mock(return_value=test_instance)

        mock_floating_ip_str = ''
        mock_floating_ip_dict = {'floating_ip_address': mock_floating_ip_str}
        self.deploy_operation.network_service.create_floating_ip = Mock(return_value=mock_floating_ip_dict)

        test_deploy_req_model = Mock()
        test_deploy_req_model.cloud_provider = test_cloud_provider
        test_deploy_req_model.add_floating_ip = True
        test_deploy_req_model.floating_ip_subnet_uuid = ''

        mock_cancellation_context = Mock()

        self.deploy_operation.instance_service.detach_floating_ip = Mock()
        self.deploy_operation.network_service.delete_floating_ip = Mock()
        self.deploy_operation.instance_service.terminate_instance = Mock()

        with self.assertRaises(ValueError) as context:
            self.deploy_operation.deploy(os_session=self.openstack_session,
                                         reservation=self.reservation,
                                         cp_resource_model=self.cp_resource_model,
                                         deploy_app_action=test_deploy_req_model,
                                         cancellation_context=mock_cancellation_context,
                                         logger=self.mock_logger)

        self.deploy_operation.instance_service.detach_floating_ip.assert_called_with(
            openstack_session=self.openstack_session,
            instance=test_instance,
            floating_ip='',
            logger=self.mock_logger)
        self.deploy_operation.instance_service.terminate_instance.assert_called_with(
            openstack_session=self.openstack_session,
            instance_id=test_id,
            logger=self.mock_logger)
        self.deploy_operation.network_service.delete_floating_ip.assert_called_with(
            openstack_session=self.openstack_session,
            floating_ip='',
            logger=self.mock_logger)
        self.assertTrue(context)
