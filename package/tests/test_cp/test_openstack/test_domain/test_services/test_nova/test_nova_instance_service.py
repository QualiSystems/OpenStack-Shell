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

        mock_deploy_req_model = Mock()
        mock_deploy_req_model.affinity_group_uuid = ''

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
                                                       deploy_req_model=mock_deploy_req_model,
                                                       logger=self.mock_logger)

        mock_client2.servers.create.assert_called_with(name=test_uniq_name,
                                                       image=mock_image,
                                                       flavor=mock_flavor,
                                                       nics=[mock_qnet_dict])
        self.assertEquals(result, mocked_inst)
        self.instance_service.instance_waiter.wait.assert_called_with(mocked_inst, state=self.instance_service.instance_waiter.ACTIVE)

    def test_instance_create_success_affinity_group(self):
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

        mock_deploy_req_model = Mock()
        mock_deploy_req_model.affinity_group_uuid = 'test_affinity_group_id'

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
                                                       deploy_req_model=mock_deploy_req_model,
                                                       logger=self.mock_logger)

        mock_client2.servers.create.assert_called_with(name=test_uniq_name,
                                                       image=mock_image,
                                                       flavor=mock_flavor,
                                                       nics=[mock_qnet_dict],
                                                       scheduler_hints={'group': 'test_affinity_group_id'})
        self.assertEquals(result, mocked_inst)
        self.instance_service.instance_waiter.wait.assert_called_with(mocked_inst, state=self.instance_service.instance_waiter.ACTIVE)


    def test_instance_terminate_openstack_session_none(self):
        with self.assertRaises(ValueError) as context:
            self.instance_service.terminate_instance(openstack_session=None,
                                                     instance_id='1234',
                                                     floating_ip = '1.2.3.4',
                                                     logger=self.mock_logger)
            self.assertTrue(context)

    def test_instance_terminate_success(self):
        mock_client2 = Mock()
        test_nova_instance_service.novaclient.Client = Mock(return_value=mock_client2)

        mock_instance = Mock()
        test_instance_id = '1234-56'
        test_floating_ip =  '1.2.3.4'
        self.instance_service.get_instance_from_instance_id = Mock(return_value=mock_instance)
        self.instance_service.detach_and_delete_floating_ip = Mock()
        self.instance_service.terminate_instance(openstack_session=self.openstack_session,
                                                 instance_id=test_instance_id,
                                                 floating_ip = test_floating_ip,
                                                 logger=self.mock_logger)

        mock_client2.servers.delete.assert_called_with(mock_instance)
        self.instance_service.detach_and_delete_floating_ip.assert_called_with(openstack_session=self.openstack_session,
                                                                               instance=mock_instance,
                                                                               floating_ip=test_floating_ip)

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

    def test_get_instance_from_instance_id_not_found_on_nova(self):
        """Check that function will return None if instance with given id will not be found on the Nova server"""
        mock_client = Mock()
        test_nova_instance_service.novaclient.Client = Mock(return_value=mock_client)

        mock_client.servers.find = Mock(side_effect=test_nova_instance_service.novaclient.exceptions.NotFound(""))

        test_instance_id = '1234'
        result = self.instance_service.get_instance_from_instance_id(openstack_session=self.openstack_session,
                                                                     instance_id=test_instance_id,
                                                                     logger=self.mock_logger,
                                                                     client=mock_client)
        self.assertEqual(result, None)

    def test_get_instance_from_instance_id_reraise_exception(self):
        """Check that function will re-raise exception if such occurs during retrieving instance from Nova server"""
        mock_client = Mock()
        test_nova_instance_service.novaclient.Client = Mock(return_value=mock_client)

        mock_client.servers.find = Mock(side_effect=Exception())
        test_instance_id = '1234'

        with self.assertRaises(Exception):
            self.instance_service.get_instance_from_instance_id(openstack_session=self.openstack_session,
                                                                instance_id=test_instance_id,
                                                                logger=self.mock_logger,
                                                                client=mock_client)

    def test_attach_nic_to_net_success(self):
        """

        :return:
        """

        import jsonpickle

        mock_client = Mock()
        test_nova_instance_service.novaclient.Client = Mock(return_value=mock_client)

        mock_instance = Mock()

        mock_iface_attach_result = Mock()
        mock_instance.interface_attach = Mock(return_value=mock_iface_attach_result)

        expected_test_mac = 'test_mac_address'
        expected_port_id = 'test_port_id'
        expected_ip_address = 'test_ip_address'
        mock_result_dict = {'mac_addr': expected_test_mac,
                            'port_id' : expected_port_id,
                            'fixed_ips' : [{'ip_address': expected_ip_address}]}
        mock_iface_attach_result.to_dict = Mock(return_value=mock_result_dict)
        self.instance_service.get_instance_from_instance_id = Mock(return_value=mock_instance)

        result = self.instance_service.attach_nic_to_net(openstack_session=self.openstack_session,
                                                         net_id='test_net_id',
                                                         instance_id='test_instance_id',
                                                         logger=self.mock_logger)
        expected_result_dict = {'ip_address':expected_ip_address,
                                'port_id': expected_port_id,
                                'mac_address':expected_test_mac}

        self.assertEqual(jsonpickle.loads(result), expected_result_dict)

    def test_attach_nic_to_net_failure_no_instance(self):

        mock_client = Mock()
        test_nova_instance_service.novaclient.Client = Mock(return_value=mock_client)

        self.instance_service.get_instance_from_instance_id = Mock(return_value=None)
        result = self.instance_service.attach_nic_to_net(openstack_session=self.openstack_session,
                                                         net_id='test_net_id',
                                                         instance_id='test_instance_id',
                                                         logger=self.mock_logger)
        self.assertEqual(result, None)

    def test_attach_nic_to_net_failure_exception(self):

        mock_client = Mock()
        test_nova_instance_service.novaclient.Client = Mock(return_value=mock_client)

        mock_instance = Mock()

        mock_instance.interface_attach = Mock(side_effect=Exception)

        result = self.instance_service.attach_nic_to_net(openstack_session=self.openstack_session,
                                                         net_id='test_net_id',
                                                         instance_id='test_instance_id',
                                                         logger=self.mock_logger)

        self.assertEqual(result, None)

    def test_detach_nic_from_net_success(self):

        mock_client = Mock()
        test_nova_instance_service.novaclient.Client = Mock(return_value=mock_client)

        mock_instance = Mock()
        self.instance_service.get_instance_from_instance_id = Mock(return_value=mock_instance)

        mock_iface_detach_result = Mock()
        mock_instance.interface_detach = Mock(return_value=mock_iface_detach_result)

        result = self.instance_service.detach_nic_from_instance(openstack_session=self.openstack_session,
                                                                instance_id='test_instance_id',
                                                                port_id='test_port_id',
                                                                logger=self.mock_logger)
        mock_instance.interface_detach.assert_called_with('test_port_id')
        self.assertEqual(result, True)

    def test_detach_nic_from_net_failure(self):

        mock_client = Mock()
        test_nova_instance_service.novaclient.Client = Mock(return_value=mock_client)

        mock_instance = Mock()
        self.instance_service.get_instance_from_instance_id = Mock(return_value=mock_instance)

        mock_instance.interface_detach = Mock(side_effect=Exception)

        result = self.instance_service.detach_nic_from_instance(openstack_session=self.openstack_session,
                                                                instance_id='test_instance_id',
                                                                port_id='test_port_id',
                                                                logger=self.mock_logger)
        self.assertEqual(result, False)

    def test_assign_floating_ip(self):
        mock_client = Mock()
        test_nova_instance_service.novaclient.Client = Mock(return_value=mock_client)

        test_external_nw_id = 'ext-net-id'
        test_floating_ip = '4.3.2.1'
        test_net_label = 'test-net'

        mock_net_obj = Mock()
        mock_net_obj.to_dict = Mock(return_value={'id':test_external_nw_id, 'label': test_net_label})

        mock_client.networks.list = Mock(return_value=[mock_net_obj])

        mock_floating_ip_obj = Mock()
        mock_floating_ip_obj.ip = test_floating_ip
        mock_client.floating_ips.create = Mock(return_value=mock_floating_ip_obj)

        mock_instance = Mock()
        mock_cp_resource_model = Mock()

        result = self.instance_service.assign_floating_ip(openstack_session=self.openstack_session,
                                                          instance=mock_instance,
                                                          cp_resource_model=mock_cp_resource_model,
                                                          floating_ip_net_uuid=test_external_nw_id,
                                                          logger=self.mock_logger)

        mock_client.floating_ips.create.assert_called_with(test_net_label)
        self.assertEqual(result, test_floating_ip)

    def test_delete_floating_ip(self):
        mock_client = Mock()
        test_nova_instance_service.novaclient.Client = Mock(return_value=mock_client)

        mock_client.floating_ips = Mock()
        mock_floating_ip_obj = Mock()
        mock_floating_ip_obj.ip = '1.2.3.4'
        mock_floating_ip_obj.id = 'test-id'
        mock_client.floating_ips.list = Mock(return_value=[mock_floating_ip_obj])

        mock_instance = Mock()
        self.instance_service.get_instance_from_instance_id = Mock(return_value=mock_instance)
        mock_instance.remove_floating_ip = Mock()

        self.instance_service.detach_and_delete_floating_ip(openstack_session=self.openstack_session,
                                                            instance=mock_instance,
                                                            floating_ip=mock_floating_ip_obj.ip)
        mock_client.floating_ips.delete.assert_called_with(mock_floating_ip_obj.id)
        mock_instance.remove_floating_ip.assert_called_with(mock_floating_ip_obj)