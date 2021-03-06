from unittest import TestCase
from mock import Mock

from cloudshell.cp.openstack.command.operations.hidden_operation import HiddenOperation


class TestHiddenOperation(TestCase):

    def setUp(self):
        self.instance_service=Mock()
        self.network_service = Mock()
        self.hidden_operation = HiddenOperation(instance_service=self.instance_service,
                                                network_service=self.network_service)
        self.hidden_operation.instance_service = Mock()
        self.hidden_operation.instance_waiter = Mock()

        self.openstack_session = Mock()
        self.cloudshell_session = Mock()
        self.mock_logger = Mock()

    def test_delete_operation_success(self):

        test_id = '1234-56'
        test_deployed_app_resource = Mock()
        test_deployed_app_resource.vmdetails.uid = test_id
        test_floating_ip = '1.2.3.4'

        mock_instance = Mock()
        self.hidden_operation.instance_service.get_instance_from_instance_id = Mock(return_value=mock_instance)

        self.hidden_operation.delete_instance(openstack_session=self.openstack_session,
                                              deployed_app_resource=test_deployed_app_resource,
                                              floating_ip=test_floating_ip,
                                              logger=self.mock_logger)

        self.hidden_operation.instance_service.terminate_instance.assert_called_with(openstack_session=self.openstack_session,
                                                                                     instance_id=test_id,
                                                                                     logger=self.mock_logger)
        self.hidden_operation.instance_service.detach_floating_ip.assert_called_with(openstack_session=self.openstack_session,
                                                                                     instance=mock_instance,
                                                                                     floating_ip=test_floating_ip,
                                                                                     logger=self.mock_logger)
        self.hidden_operation.network_service.delete_floating_ip.assrt_called_with(openstack_session=self.openstack_session,
                                                                                   floating_ip=test_floating_ip,
                                                                                   logger=self.mock_logger)


    def test_delete_operation_exception(self):
        test_id = '1234-56'
        test_deployed_app_resource = Mock()
        test_deployed_app_resource.vmdetails.uid = test_id

        self.hidden_operation.instance_service.terminate_instance = Mock(side_effect=Exception("XXX"))
        with self.assertRaises(Exception) as context:
            self.hidden_operation.delete_instance(openstack_session=self.openstack_session,
                                                  deployed_app_resource=test_deployed_app_resource,floating_ip='',
                                                  logger=self.mock_logger)
            self.assertTrue(context)

