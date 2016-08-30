from unittest import TestCase
from mock import Mock, patch

from cloudshell.cp.openstack.domain.services.nova.nova_instance_service import NovaInstanceService
import cloudshell.cp.openstack.domain.services.nova.nova_instance_service as test_nova_instance_service


class TestNovaInstanceService(TestCase):
    def setUp(self):
        instance_waiter = Mock()
        instance_waiter.wait = Mock()
        self.instance_service = NovaInstanceService(instance_waiter=instance_waiter)
        self.mock_logger = Mock()
        self.openstack_session = Mock()

    def test_instance_create_empty_openstack_session(self):
        test_name = 'test'
        result = self.instance_service.create_instance(openstack_session=None,
                                                       name=test_name,
                                                       reservation=Mock(),
                                                       deploy_req_model=Mock(),
                                                       logger=self.mock_logger)
        self.assertEqual(result, None)

    def test_instance_create_success(self):
        test_name = 'test'
        mock_client2 = Mock()

        test_nova_instance_service.novaclient.Client = Mock(return_value=mock_client2)
        # mock_client.Client = Mock(return_vaule=mock_client2)
        mock_client2.images.find = Mock(return_value=Mock())
        mock_client2.flavors.find = Mock(return_value=Mock())

        mock_netobj = Mock()
        mock_client2.networks.find = Mock(return_type=mock_netobj)
        mock_client2.servers = Mock()
        mocked_inst = Mock()
        mock_client2.servers.create = Mock(return_value=mocked_inst)
        mock_qnet_dict = {'qnet-id': mock_netobj}
        result = self.instance_service.create_instance(openstack_session=self.openstack_session,
                                                       name=test_name,
                                                       reservation=Mock(),
                                                       deploy_req_model=Mock(),
                                                       logger=self.mock_logger)

        mock_client2.servers.create.assert_called()
        # FIXME : Assert called_with
        self.assertEquals(result, mocked_inst)

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
