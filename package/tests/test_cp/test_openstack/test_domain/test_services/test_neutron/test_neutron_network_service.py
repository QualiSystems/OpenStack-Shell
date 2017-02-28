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

    def test_valid_cidr_returned(self):

        mock_client = Mock()
        test_neutron_network_service.neutron_client.Client = Mock(return_value=mock_client)
        mock_client.create_subnet = Mock(return_value={'subnet': 'subnet success'})

        mock_return_subnets = {'subnets': [{'cidr': '10.0.0.0/24', 'id': 'test-id-1'},
                                           {'cidr': '10.0.1.0/24', 'id': 'test-id-2'}]}

        test_reserved_subnets = '172.0.0.0/8, 192.168.0.0/24'
        mock_client.list_subnets = Mock(return_value=mock_return_subnets)
        result = self.network_service._get_unused_cidr(client=mock_client,
                                                       cp_resvd_cidrs=test_reserved_subnets,
                                                       logger=self.mock_logger)
        self.assertEqual(result, '10.0.2.0/24')

    def test_none_cidr_returned(self):
        mock_client = Mock()
        test_neutron_network_service.neutron_client.Client = Mock(return_value=mock_client)
        mock_client.create_subnet = Mock(return_value={'subnet': 'subnet success'})

        mock_return_subnets = {'subnets': [{'cidr': '10.0.0.0/24', 'id': 'test-id-1'},
                                           {'cidr': '10.0.1.0/24', 'id': 'test-id-2'}]}

        test_reserved_subnets = '10.0.0.0/8, 172.16.0.0/12 , 192.168.0.0/16'
        mock_client.list_subnets = Mock(return_value=mock_return_subnets)
        result = self.network_service._get_unused_cidr(client=mock_client,
                                                       cp_resvd_cidrs=test_reserved_subnets,
                                                       logger=self.mock_logger)
        self.assertEqual(result, None)

    def test_empty_reserved_networks(self):
        mock_client = Mock()
        test_neutron_network_service.neutron_client.Client = Mock(return_value=mock_client)
        mock_client.create_subnet = Mock(return_value={'subnet': 'subnet success'})

        mock_return_subnets = {'subnets': [{'cidr': '10.0.0.0/24', 'id': 'test-id-1'},
                                           {'cidr': '10.0.1.0/24', 'id': 'test-id-2'}]}

        test_reserved_subnets = ''
        mock_client.list_subnets = Mock(return_value=mock_return_subnets)
        result = self.network_service._get_unused_cidr(client=mock_client,
                                                       cp_resvd_cidrs=test_reserved_subnets,
                                                       logger=self.mock_logger)
        self.assertEqual(result, '10.0.2.0/24')

    def test_reserved_networks_one_empty_entry(self):
        mock_client = Mock()
        test_neutron_network_service.neutron_client.Client = Mock(return_value=mock_client)
        mock_client.create_subnet = Mock(return_value={'subnet': 'subnet success'})

        mock_return_subnets = {'subnets': [{'cidr': '10.0.0.0/24', 'id': 'test-id-1'},
                                           {'cidr': '10.0.1.0/24', 'id': 'test-id-2'}]}

        test_reserved_subnets = '172.16.0.0/12,,192.168.0.0/16'
        mock_client.list_subnets = Mock(return_value=mock_return_subnets)
        result = self.network_service._get_unused_cidr(client=mock_client,
                                                       cp_resvd_cidrs=test_reserved_subnets,
                                                       logger=self.mock_logger)
        self.assertEqual(result, '10.0.2.0/24')

    def test_create_and_attach_subnet_to_net_success(self):

        test_net_id = 'test-net-id'
        mock_client = Mock()
        test_neutron_network_service.neutron_client.Client = Mock(return_value=mock_client)
        mock_client.create_subnet = Mock(return_value={'subnet':'subnet success'})

        mock_return_subnets = {'subnets':[{'cidr': '192.168.1.0/24', 'id':'test-id-1'},
                               {'cidr': '192.168.1.0/24', 'id': 'test-id-2'}]}

        test_reserved_subnets = '10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/24'
        mock_client.list_subnets = Mock(return_value=mock_return_subnets)

        cp_resource_model = Mock()
        cp_resource_model.reserved_networks = test_reserved_subnets
        # self.network_service._get_unused_cidr = Mock(return_value = '10.0.0.0/24')

        result = self.network_service.create_and_attach_subnet_to_net(openstack_session=self.openstack_session,
                                                                      cp_resource_model=cp_resource_model,
                                                                      net_id=test_net_id,
                                                                      logger=self.mock_logger)
        self.assertEqual(result, 'subnet success')

    def test_create_and_attach_subnet_to_net_return_none(self):

        test_net_id = 'test-net-id'
        mock_client = Mock()
        test_neutron_network_service.neutron_client.Client = Mock(return_value=mock_client)
        mock_client.create_subnet = Mock(side_effect=Exception)

        self.network_service._get_unused_cidr = Mock(return_value = '10.0.0.0/24')

        with self.assertRaises(Exception) as context:
            result = self.network_service.create_and_attach_subnet_to_net(openstack_session=self.openstack_session,
                                                                      cp_resource_model=Mock(),
                                                                      net_id=test_net_id,
                                                                      logger=self.mock_logger)
        self.assertTrue(context)

    def test_create_floating_ip_success(self):

        mock_client = Mock()
        test_neutron_network_service.neutron_client.Client = Mock(return_value=mock_client)

        test_network_id = 'test_network_id'
        test_subnet_id = 'test_subnet_id'
        test_result_subnet_dict = {'subnets': [{'network_id':test_network_id}]}

        mock_client.list_subnets = Mock(return_value=test_result_subnet_dict)

        test_floating_ip = '1.2.3.4'
        test_floating_ip_dict = {'floatingip':test_floating_ip}

        mock_client.create_floatingip = Mock(return_value=test_floating_ip_dict)

        result = self.network_service.create_floating_ip(openstack_session=self.openstack_session,
                                                         floating_ip_subnet_id=test_subnet_id,
                                                         logger=self.mock_logger)

        floating_ip_call_dict = {'floatingip': {'floating_network_id':test_network_id, 'subnet_id':test_subnet_id}}
        mock_client.create_floatingip.assert_called_with(floating_ip_call_dict)
        self.assertEqual(result, test_floating_ip)

    def test_create_floating_ip_returns_None(self):

        mock_client = Mock()
        test_neutron_network_service.neutron_client.Client = Mock(return_value=mock_client)

        test_network_id = 'test_network_id'
        test_subnet_id = 'test_subnet_id'
        test_result_subnet_dict = {'subnets': [{'network_id':test_network_id}]}

        mock_client.list_subnets = Mock(return_value=test_result_subnet_dict)

        mock_client.create_floatingip = Mock(return_value={})

        result = self.network_service.create_floating_ip(openstack_session=self.openstack_session,
                                                         floating_ip_subnet_id=test_subnet_id,
                                                         logger=self.mock_logger)

        floating_ip_call_dict = {'floatingip': {'floating_network_id':test_network_id, 'subnet_id':test_subnet_id}}
        mock_client.create_floatingip.assert_called_with(floating_ip_call_dict)
        self.assertEqual(result, None)

    def test_delete_floating_ip_success(self):

        mock_client = Mock()
        test_neutron_network_service.neutron_client.Client = Mock(return_value=mock_client)

        test_floating_ip = '1.2.3.4'
        test_floating_ip_id = 'test_floating_id'

        mock_list_result_dict = {'floatingips': [{'id': test_floating_ip_id}]}
        mock_client.list_floatingips = Mock(return_value=mock_list_result_dict)

        mock_client.delete_floatingip = Mock()

        result = self.network_service.delete_floating_ip(openstack_session=self.openstack_session,
                                                         floating_ip=test_floating_ip,
                                                         logger=self.mock_logger)

        mock_client.delete_floatingip.assert_called_with(test_floating_ip_id)
        self.assertTrue(result)

    def test_delete_floating_ip_false(self):

        mock_client = Mock()
        test_neutron_network_service.neutron_client.Client = Mock(return_value=mock_client)

        test_floating_ip = ''

        mock_client.delete_floatingip = Mock()

        result = self.network_service.delete_floating_ip(openstack_session=self.openstack_session,
                                                         floating_ip=test_floating_ip,
                                                         logger=self.mock_logger)
        mock_client.delete_floatingip.assert_not_called()
        self.assertFalse(result)