from functools import partial
from unittest import TestCase

from mock import Mock, MagicMock, patch

from cloudshell.cp.openstack.domain.services.waiters.instance import InstanceWaiter
from cloudshell.cp.openstack.models.exceptions import InstanceErrorStateException


class TestTaskWaiterService(TestCase):
    def setUp(self):
        self.cancellation_service = Mock()
        self.instance_waiter_service = InstanceWaiter(cancellation_service=self.cancellation_service)

    @patch("cloudshell.cp.openstack.domain.services.waiters.instance.time.sleep")
    def test_wait_for_instance_active(self, sleep):
        def instance_status_changer(instance_obj, new_state):
            instance_obj.status = new_state

        # Arrange
        cancellation_context = Mock()
        instance = Mock()
        instance.status = None
        instance_status_changer_command = partial(instance_status_changer,
                                                  instance,
                                                  self.instance_waiter_service.ACTIVE)
        instance.get = MagicMock(side_effect=instance_status_changer_command)

        # Act
        result = self.instance_waiter_service.wait(instance=instance,
                                                   state=self.instance_waiter_service.ACTIVE,
                                                   cancellation_context=cancellation_context,
                                                   logger=Mock)

        # Verify
        instance.get.assert_called_once()
        self.cancellation_service.check_if_cancelled.assert_called_once_with(cancellation_context=cancellation_context)
        sleep.assert_called_once_with(self.instance_waiter_service._delay)
        self.assertEquals(result, instance)

    @patch("cloudshell.cp.openstack.domain.services.waiters.instance.time.sleep")
    def test_wait_for_instance_error(self, sleep):
        def instance_status_changer(instance_obj, new_state):
            instance_obj.status = new_state

        # Arrange
        cancellation_context = Mock()
        instance = MagicMock()
        instance.fault['message'] = "bb"
        instance.status = None
        instance_status_changer_command = partial(instance_status_changer,
                                                  instance,
                                                  self.instance_waiter_service.ERROR)
        instance.get = MagicMock(side_effect=instance_status_changer_command)

        with self.assertRaises(InstanceErrorStateException) as context:
            result = self.instance_waiter_service.wait(instance=instance,
                                                       state=self.instance_waiter_service.ERROR,
                                                       cancellation_context=cancellation_context,
                                                       logger=Mock)

        # Verify
        instance.get.assert_called_once()
        self.assertEquals(context.exception.message, str(instance.fault['message']))
