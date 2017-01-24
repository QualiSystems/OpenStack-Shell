from unittest import TestCase
from mock import Mock

from cloudshell.cp.openstack.command.operations.refresh_ip_operation import RefreshIPOperation

class TestRefreshIPOperation(TestCase):
    def setUp(self):
        self.cancellation_service = Mock()
        self.refresh_ip_operation = RefreshIPOperation(cancellation_service=self.cancellation_service)
        self.refresh_ip_operation.instance_service = Mock()

        self.openstack_session = Mock()
        self.cloudshell_session = Mock()
        self.deployed_app_resource = Mock()
        self.test_uid = '111'
        self.deployed_app_resource.vmdetails.uid = self.test_uid
        self.mock_logger = Mock()
        self.resource_fullname = 'Resource Fullname'
        self.private_ip = '1.2.3.4'
        self.cp_resource_model = Mock()

    def test_refresh_ip_operation_refresh_ip_normal(self):

        self.refresh_ip_operation.instance_service.get_private_ip = Mock(return_value=self.private_ip)

        self.refresh_ip_operation.refresh_ip(openstack_session=self.openstack_session,
                                             cloudshell_session=self.cloudshell_session,
                                             deployed_app_resource=self.deployed_app_resource,
                                             private_ip=self.private_ip,
                                             resource_fullname=self.resource_fullname,
                                             cp_resource_model=self.cp_resource_model,
                                             logger=self.mock_logger)

        self.refresh_ip_operation.instance_service.get_instance_from_instance_id.assert_called_with(
                openstack_session=self.openstack_session,
                instance_id=self.test_uid,
                logger=self.mock_logger)

        self.assertFalse(self.cloudshell_session.UpdateResourceAddress.called)

    def test_refresh_ip_operation_refresh_ip_existing_ip(self):

        self.refresh_ip_operation.instance_service.get_private_ip = Mock(return_value="4.3.2.1")

        self.refresh_ip_operation.refresh_ip(openstack_session=self.openstack_session,
                                             cloudshell_session=self.cloudshell_session,
                                             deployed_app_resource=self.deployed_app_resource,
                                             private_ip=self.private_ip,
                                             resource_fullname=self.resource_fullname,
                                             cp_resource_model=self.cp_resource_model,
                                             logger=self.mock_logger)

        self.refresh_ip_operation.instance_service.get_instance_from_instance_id.assert_called_with(
            openstack_session=self.openstack_session,
            instance_id=self.test_uid,
            logger=self.mock_logger)

        self.cloudshell_session.UpdateResourceAddress.assert_called()


    def test_refresh_ip_operation_refresh_ip_no_instance(self):

        self.refresh_ip_operation.instance_service.get_instance_from_instance_id = Mock(return_value=None)

        with self.assertRaises(ValueError) as context:
            self.refresh_ip_operation.refresh_ip(openstack_session=self.openstack_session,
                                                 cloudshell_session=self.cloudshell_session,
                                                 deployed_app_resource=self.deployed_app_resource,
                                                 private_ip=self.private_ip,
                                                 resource_fullname=self.resource_fullname,
                                                 cp_resource_model=self.cp_resource_model,
                                                 logger=self.mock_logger)
            self.assertTrue(context)

        self.refresh_ip_operation.instance_service.get_instance_from_instance_id.assert_called_with(
            openstack_session=self.openstack_session,
            instance_id=self.test_uid,
            logger=self.mock_logger)

        self.assertFalse(self.cloudshell_session.SetAttributeValue.called)
