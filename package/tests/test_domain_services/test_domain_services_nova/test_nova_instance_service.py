from unittest import TestCase
from mock import Mock

from cloudshell.cp.openstack.domain.services.nova.nova_instance_service import NovaInstanceService
import cloudshell.cp.openstack.domain.services.nova.nova_instance_service as test_nova_instance_service
from cloudshell.cp.openstack.common.driver_helper import CloudshellDriverHelper

class TestNovaInstanceService(TestCase):
    def setUp(self):
        instance_waiter = Mock()
        instance_waiter.wait = Mock()
        instance_waiter.ACTIVE = 'ACTIVE'
        self.instance_service = NovaInstanceService(instance_waiter=instance_waiter)
        self.mock_logger = Mock()
        self.openstack_session = Mock()

    def test_instance_create_empty_openstack_session(self):
        test_name = 'test'
        result = self.instance_service.create_instance(openstack_session=None,
                                                       name=test_name,
                                                       reservation=Mock(),
                                                       cp_resource_model=Mock(),
                                                       deploy_req_model=Mock(),
                                                       logger=self.mock_logger)
        self.assertEqual(result, None)

    def test_instance_create_success(self):
        test_name = 'test'
        CloudshellDriverHelper.get_uuid = Mock(return_value='1234')
        test_uniq_name = 'test-1234'
        mock_client2 = Mock()

        test_nova_instance_service.novaclient.Client = Mock(return_value=mock_client2)
        # mock_client.Client = Mock(return_vaule=mock_client2)
        mock_image = Mock()
        mock_flavor = Mock()
        mock_client2.images.find = Mock(return_value=mock_image)
        mock_client2.flavors.find = Mock(return_value=mock_flavor)

        mock_cp_resource_model = Mock()
        mock_cp_resource_model.qs_mgmt_os_net_uuid = '1234'

        mock_client2.servers = Mock()
        mocked_inst = Mock()
        mock_client2.servers.create = Mock(return_value=mocked_inst)
        mock_qnet_dict = {'net-id': mock_cp_resource_model.qs_mgmt_os_net_uuid}
        result = self.instance_service.create_instance(openstack_session=self.openstack_session,
                                                       name=test_name,
                                                       reservation=Mock(),
                                                       cp_resource_model=mock_cp_resource_model,
                                                       deploy_req_model=Mock(),
                                                       logger=self.mock_logger)

        mock_client2.servers.create.assert_called_with(name=test_uniq_name,
                                                       image=mock_image,
                                                       flavor=mock_flavor,
                                                       nics=[mock_qnet_dict])
        self.assertEquals(result, mocked_inst)
        self.instance_service.instance_waiter.wait.assert_called_with(mocked_inst, state=self.instance_service.instance_waiter.ACTIVE)

    def test_instance_terminate_openstack_session_none(self):
        with self.assertRaises(ValueError) as context:
            self.instance_service.terminate_instance(openstack_session=None,
                                                     instance_id='1234',
                                                     logger=self.mock_logger)
            self.assertTrue(context)

    def test_instance_terminate_success(self):
        mock_client2 = Mock()
        test_nova_instance_service.novaclient.Client = Mock(return_value=mock_client2)

        mock_instance = Mock()
        test_instance_id = '1234-56'
        self.instance_service.get_instance_from_instance_id = Mock(return_value=mock_instance)
        self.instance_service.terminate_instance(openstack_session=self.openstack_session,
                                                 instance_id=test_instance_id,
                                                 logger=self.mock_logger)

        mock_client2.servers.delete.assert_called_with(mock_instance)



    def test_instance_power_off_success(self):
        mock_client2 = Mock()
        test_nova_instance_service.novaclient.Client = Mock(return_value=mock_client2)

        mock_instance = Mock()
        test_instance_id = '1234-56'
        self.instance_service.get_instance_from_instance_id = Mock(return_value=mock_instance)
        self.instance_service.instance_power_off(openstack_session=self.openstack_session,
                                                 instance_id=test_instance_id,
                                                 logger=self.mock_logger)

        self.instance_service.get_instance_from_instance_id.assert_called_with(openstack_session=self.openstack_session,
                                                                               instance_id=test_instance_id,
                                                                               logger=self.mock_logger,
                                                                               client=mock_client2)
        self.assertEqual(True, mock_instance.stop.called)

    def test_instance_power_on_success(self):
        mock_client2 = Mock()
        test_nova_instance_service.novaclient.Client = Mock(return_value=mock_client2)

        mock_instance = Mock()
        test_instance_id = '1234-56'
        self.instance_service.get_instance_from_instance_id = Mock(return_value=mock_instance)
        self.instance_service.instance_power_on(openstack_session=self.openstack_session,
                                                instance_id=test_instance_id,
                                                logger=self.mock_logger)

        self.instance_service.get_instance_from_instance_id.assert_called_with(openstack_session=self.openstack_session,
                                                                               instance_id=test_instance_id,
                                                                               logger=self.mock_logger,
                                                                               client=mock_client2)
        self.assertEqual(True, mock_instance.start.called)

    def test_get_instance_from_instance_id(self):
        mock_client2 = Mock()
        test_nova_instance_service.novaclient.Client = Mock(return_value=mock_client2)

        mock_instance = Mock()
        mock_client2.servers.find = Mock(return_value=mock_instance)

        test_instance_id = '1234'
        result = self.instance_service.get_instance_from_instance_id(openstack_session=self.openstack_session,
                                                            instance_id=test_instance_id,
                                                            logger=self.mock_logger,
                                                            client=mock_client2)
        self.assertEqual(result, mock_instance)