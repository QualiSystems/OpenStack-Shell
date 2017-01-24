from unittest import TestCase
from mock import Mock

from cloudshell.cp.openstack.command.operations.power_operation import PowerOperation


class TestPowerOperation(TestCase):
    def setUp(self):
        self.cancellation_service = Mock()
        self.power_operation = PowerOperation(cancellation_service=self.cancellation_service)
        self.power_operation.instance_waiter = Mock()
        self.power_operation.instance_service = Mock()
        self.openstack_session = Mock()
        self.cloudshell_session = Mock()

    def test_power_on_instance_not_powered(self):

        deployed_app_resource = Mock()
        # deployed_app_resource.vmdetails = Mock()
        deployed_app_resource.vmdetails.uid = '111'
        resource_fullname = '1234'
        mock_logger = Mock()

        self.cloudshell_session.SetResourceLiveStatus = Mock()
        self.power_operation.power_on(openstack_session=self.openstack_session,
                                      cloudshell_session=self.cloudshell_session,
                                      deployed_app_resource=deployed_app_resource,
                                      resource_fullname=resource_fullname,
                                      logger=mock_logger)

        self.power_operation.instance_service.instance_power_on.assert_called_with(openstack_session=self.openstack_session,
                                                                                   instance_id=deployed_app_resource.vmdetails.uid,
                                                                                   logger=mock_logger)

        self.cloudshell_session.SetResourceLiveStatus.assert_called_with(resource_fullname, "Online", "Active")

    def test_power_on_instance_exception(self):
        deployed_app_resource = Mock()
        # deployed_app_resource.vmdetails = Mock()
        deployed_app_resource.vmdetails.uid = '111'
        resource_fullname = '1234'
        mock_logger = Mock()

        self.power_operation.instance_service.instance_power_on = Mock(side_effect=Exception('foo'))

        with self.assertRaises(Exception) as context:
            self.power_operation.power_on(openstack_session=self.openstack_session,
                                          cloudshell_session=self.cloudshell_session,
                                          deployed_app_resource=deployed_app_resource,
                                          resource_fullname=resource_fullname,
                                          logger=mock_logger)
            self.assertTrue(context)

        self.power_operation.instance_service.instance_power_on.assert_called_with(openstack_session=self.openstack_session,
                                                                                   instance_id=deployed_app_resource.vmdetails.uid,
                                                                                   logger=mock_logger)
        self.cloudshell_session.SetResourceLiveStatus.assert_called_with(resource_fullname, "Error", "foo")
        self.assertTrue(mock_logger.error.called)

    def test_power_off_instance_not_powered(self):
        deployed_app_resource = Mock()
        # deployed_app_resource.vmdetails = Mock()
        deployed_app_resource.vmdetails.uid = '111'
        resource_fullname = '1234'
        mock_logger = Mock()

        self.cloudshell_session.SetResourceLiveStatus = Mock()
        self.power_operation.power_off(openstack_session=self.openstack_session,
                                      cloudshell_session=self.cloudshell_session,
                                      deployed_app_resource=deployed_app_resource,
                                      resource_fullname=resource_fullname,
                                      logger=mock_logger)

        self.power_operation.instance_service.instance_power_off.assert_called_with(openstack_session=self.openstack_session,
                                                                                   instance_id=deployed_app_resource.vmdetails.uid,
                                                                                   logger=mock_logger)

        self.cloudshell_session.SetResourceLiveStatus.assert_called_with(resource_fullname, "Offline", "Powered Off")

    def test_power_off_instance_exception(self):
        deployed_app_resource = Mock()
        # deployed_app_resource.vmdetails = Mock()
        deployed_app_resource.vmdetails.uid = '111'
        resource_fullname = '1234'
        mock_logger = Mock()

        self.power_operation.instance_service.instance_power_off = Mock(side_effect=Exception('foo'))

        with self.assertRaises(Exception) as context:
            self.power_operation.power_off(openstack_session=self.openstack_session,
                                          cloudshell_session=self.cloudshell_session,
                                          deployed_app_resource=deployed_app_resource,
                                          resource_fullname=resource_fullname,
                                          logger=mock_logger)
            self.assertTrue(context)

        self.power_operation.instance_service.instance_power_off.assert_called_with(openstack_session=self.openstack_session,
                                                                                   instance_id=deployed_app_resource.vmdetails.uid,
                                                                                   logger=mock_logger)
        self.cloudshell_session.SetResourceLiveStatus.assert_called_with(resource_fullname, "Error", "foo")
        self.assertTrue(mock_logger.error.called)

