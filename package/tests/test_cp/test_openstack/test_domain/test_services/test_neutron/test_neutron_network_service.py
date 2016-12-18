from cloudshell.cp.openstack.domain.services.neutron.neutron_network_service import NeutronNetworkService
import cloudshell.cp.openstack.domain.services.neutron.neutron_network_service as test_neutron_network_service

from unittest import TestCase
from mock import Mock


class TestNeutronNetworkService(TestCase):
    def setUp(self):
        self.network_service = NeutronNetworkService()
        self.mock_logger = Mock()
        self.openstack_session = Mock()
        self.moc_cp_model = Mock()

    def test_create_or_get_network_with_segmentation_id_no_conflict(self):
        """
        Tests a successful operation of network creation with no NetCreateConflict error
        :return:
        """
        test_segmentation_id = '42'
        mock_client = Mock()
        test_neutron_network_service.neutron_client.Client = Mock(return_value=mock_client)

        mock_client.create_network = Mock(return_value={'network':'test_network'})
        result = self.network_service.create_or_get_network_with_segmentation_id(openstack_session=self.openstack_session,
                                                                                 segmentation_id=test_segmentation_id,
                                                                                 cp_resource_model=self.moc_cp_model,
                                                                                 logger=self.mock_logger)

        self.assertEqual(result, 'test_network')

    def test_create_or_get_network_with_segmentation_id_conflict(self):

        test_segmentation_id = '42'
        mock_client = Mock()
        test_neutron_network_service.neutron_client.Client = Mock(return_value=mock_client)
        mock_client.create_network = Mock(side_effect=test_neutron_network_service.NetCreateConflict)
        mock_client.list_networks = Mock(return_value={'networks': ['test_network']})

        result = self.network_service.create_or_get_network_with_segmentation_id(openstack_session=self.openstack_session,
                                                                                 segmentation_id=test_segmentation_id,
                                                                                 cp_resource_model=self.moc_cp_model,
                                                                                 logger=self.mock_logger)

        self.assertEqual(result, 'test_network')

    def test_get_network_with_segmentation_id_valid_network(self):

        test_segmentation_id = '42'
        mock_client = Mock()
        test_neutron_network_service.neutron_client.Client = Mock(return_value=mock_client)

        mock_client.list_networks = Mock(return_value={'networks': ['test_network']})

        result = self.network_service.get_network_with_segmentation_id(openstack_session=self.openstack_session,
                                                                       segmentation_id=test_segmentation_id,
                                                                       logger=self.mock_logger)
        self.assertEqual(result, 'test_network')


    def test_get_network_with_segmentation_id_no_network(self):
        test_segmentation_id = '42'
        mock_client = Mock()
        test_neutron_network_service.neutron_client.Client = Mock(return_value=mock_client)

        mock_client.list_networks = Mock(return_value={'networks': []})

        result = self.network_service.get_network_with_segmentation_id(openstack_session=self.openstack_session,
                                                                       segmentation_id=test_segmentation_id,
                                                                       logger=self.mock_logger)
        self.assertEqual(result, None)

    def test_create_and_attach_subnet_to_net_success(self):

        test_net_id = 'test-net-id'
        mock_client = Mock()
        test_neutron_network_service.neutron_client.Client = Mock(return_value=mock_client)
        mock_client.create_subnet = Mock(return_value={'subnet':'subnet success'})

        self.network_service._get_unused_cidr = Mock(return_value = '10.0.0.0/24')

        result = self.network_service.create_and_attach_subnet_to_net(openstack_session=self.openstack_session,
                                                                      cp_resource_model=Mock(),
                                                                      net_id=test_net_id,
                                                                      logger=self.mock_logger)
        self.assertEqual(result, 'subnet success')

    def test_create_and_attach_subnet_to_net_return_none(self):

        test_net_id = 'test-net-id'
        mock_client = Mock()
        test_neutron_network_service.neutron_client.Client = Mock(return_value=mock_client)
        mock_client.create_subnet = Mock(return_value=None)

        self.network_service._get_unused_cidr = Mock(return_value = '10.0.0.0/24')

        result = self.network_service.create_and_attach_subnet_to_net(openstack_session=self.openstack_session,
                                                                      cp_resource_model=Mock(),
                                                                      net_id=test_net_id,
                                                                      logger=self.mock_logger)
        self.assertEqual(result, None)