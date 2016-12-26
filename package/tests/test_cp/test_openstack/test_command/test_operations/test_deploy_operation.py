from unittest import TestCase
from mock import Mock

from cloudshell.cp.openstack.command.operations.deploy_operation import DeployOperation
from cloudshell.cp.openstack.models.deploy_result_model import DeployResultModel

class TestDeployOperation(TestCase):
    def setUp(self):
        self.deploy_operation = DeployOperation()
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
        mock_deploy_result = DeployResultModel(vm_name=test_name,
                                               vm_uuid=test_id,
                                               cloud_provider_name=test_cloud_provider,
                                               deployed_app_ip=test_private_ip)

        self.deploy_operation.instance_service.get_private_ip = Mock(return_value=test_private_ip)

        test_instance = Mock()
        test_instance.name = test_name
        test_instance.id = test_id

        self.deploy_operation.instance_service.create_instance = Mock(return_value=test_instance)

        test_deploy_req_model = Mock()
        test_deploy_req_model.cloud_provider = test_cloud_provider

        test_result = self.deploy_operation.deploy(os_session=self.openstack_session,
                                                   name=test_name,
                                                   reservation=self.reservation,
                                                   cp_resource_model=self.cp_resource_model,
                                                   deploy_req_model=test_deploy_req_model,
                                                   logger=self.mock_logger)

        self.assertEqual(test_result.vm_name, test_name)
        self.assertEqual(test_result.vm_uuid, test_id)
        self.assertEqual(test_result.cloud_provider_resource_name, test_cloud_provider)
        self.assertEqual(test_result.deployed_app_address, test_private_ip)
