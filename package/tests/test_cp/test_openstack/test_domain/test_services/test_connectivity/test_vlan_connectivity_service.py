from unittest import TestCase
from mock import Mock

from cloudshell.cp.openstack.domain.services.connectivity.vlan_connectivity_service import VLANConnectivityService
from cloudshell.cp.openstack.models.connectivity_action_resource_info import ConnectivityActionResourceInfo

from cloudshell.cp.openstack.common.deploy_data_holder import DeployDataHolder
import jsonpickle

class TestVlanConnectivityService(TestCase):
    def setUp(self):
        self.connectivity_service = VLANConnectivityService()

        self.os_session = Mock()
        self.mock_logger = Mock()

    def test_set_vlan_actions_net_create_or_get_fail(self):

        mock_cp_resource_model = Mock()
        mock_test_value = 'test_value'
        test_vlan_actions = {1 : mock_test_value, 2: mock_test_value}

        self.connectivity_service.network_service.create_or_get_network_with_segmentation_id = Mock(return_value=None)
        self.connectivity_service.set_fail_results = Mock(return_value='fail_result')

        results = self.connectivity_service.set_vlan_actions(openstack_session=self.os_session,
                                                             cp_resource_model=mock_cp_resource_model,
                                                             vlan_actions=test_vlan_actions,
                                                             logger=self.mock_logger)

        assert self.connectivity_service.set_fail_results.call_count == 2
        self.assertTrue(results, ['fail_result', 'fail_result'])

    def test_set_vlan_actions_net_create_or_get_success_no_subnet_subnet_create_fail(self):

        mock_cp_resource_model = Mock()
        mock_test_value = 'test_value'
        test_vlan_actions = {1 : mock_test_value, 2: mock_test_value}

        mock_create_or_get_result = {'id': 'test_net_id', 'subnets' : []}
        self.connectivity_service.network_service.create_or_get_network_with_segmentation_id = Mock(
                                return_value=mock_create_or_get_result)

        self.connectivity_service.network_service.create_and_attach_subnet_to_net = Mock(return_value=None)
        self.connectivity_service.set_fail_results = Mock(return_value='fail_result')

        results = self.connectivity_service.set_vlan_actions(openstack_session=self.os_session,
                                                             cp_resource_model=mock_cp_resource_model,
                                                             vlan_actions=test_vlan_actions,
                                                             logger=self.mock_logger)
        self.connectivity_service.set_fail_results.assert_any_call(values='test_value',
                                                                   action_type='setVlan',
                                                                   failure_text='Failed to attach Subnet to Network test_net_id')
        assert self.connectivity_service.set_fail_results.call_count == 2
        self.assertTrue(results, ['fail_result', 'fail_result'])

    def test_set_vlan_actions_net_create_or_get_success_subnet_success(self):

        mock_cp_resource_model = Mock()
        mock_test_value = 'test_value'
        test_vlan_actions = {1 : mock_test_value, 2: mock_test_value}

        mock_create_or_get_result = {'id': 'test_net_id', 'subnets' : []}
        self.connectivity_service.network_service.create_or_get_network_with_segmentation_id = Mock(
                                return_value=mock_create_or_get_result)

        self.connectivity_service.network_service.create_and_attach_subnet_to_net = Mock(return_value='test_subnet')
        self.connectivity_service.attach_nic_to_instance_action_result = Mock(return_value='Success')

        results = self.connectivity_service.set_vlan_actions(openstack_session=self.os_session,
                                                             cp_resource_model=mock_cp_resource_model,
                                                             vlan_actions=test_vlan_actions,
                                                             logger=self.mock_logger)
        self.assertTrue(results, ['Success', 'Success'])

    def test_remove_vlan_actions_get_network_service_no_net(self):

        mock_cp_resource_model = Mock()
        mock_test_value = 'test_value'
        test_vlan_actions = {1: mock_test_value, 2: mock_test_value}

        self.connectivity_service.network_service.get_network_with_segmentation_id = Mock(return_value=None)
        self.connectivity_service.set_fail_results = Mock(return_value='fail_result')

        results = self.connectivity_service.remove_vlan_actions(openstack_session=self.os_session,
                                                             cp_resource_model=mock_cp_resource_model,
                                                             vlan_actions=test_vlan_actions,
                                                             logger=self.mock_logger)

        assert self.connectivity_service.set_fail_results.call_count == 2
        self.assertTrue(results, ['fail_result', 'fail_result'])

    def test_remove_vlan_actions_get_network_service_net_found(self):
        mock_cp_resource_model = Mock()
        mock_test_value = 'test_value'
        test_vlan_actions = {1: mock_test_value, 2: mock_test_value}

        mock_get_network_with_vlanid_result = {'id' : 'test-net-id'}
        self.connectivity_service.network_service.get_network_with_segmentation_id = Mock(
                        return_value=mock_get_network_with_vlanid_result)
        self.connectivity_service.detach_nic_from_instance_action_result = Mock(return_value='Success')
        self.connectivity_service.network_service.remove_subnet_and_net = Mock()

        results = self.connectivity_service.remove_vlan_actions(openstack_session=self.os_session,
                                                                cp_resource_model=mock_cp_resource_model,
                                                                vlan_actions=test_vlan_actions,
                                                                logger=self.mock_logger)

        self.connectivity_service.network_service.remove_subnet_and_net.assert_called_with(
                        openstack_session=self.os_session,
                        network=mock_get_network_with_vlanid_result,
                        logger=self.mock_logger)

        self.assertTrue(results, ['Success', 'Success'])

    def test_set_fail_results(self):
        mock_action_resource_info = ConnectivityActionResourceInfo(deployed_app_resource_name='test_app',
                                                                   actionid='test-actionid',
                                                                   vm_uuid='test-vm-uuid',
                                                                   interface_ip='test-ip',
                                                                   interface_port_id='test-port-id',
                                                                   interface_mac='test-mac')

        mock_values = [mock_action_resource_info]
        mock_failure_text = 'test failure test'
        mock_action_type = 'test action'

        results = self.connectivity_service.set_fail_results(values=mock_values,
                                                            failure_text=mock_failure_text,
                                                            action_type=mock_action_type,
                                                            logger=None)
        result = results[0]

        self.assertTrue(result.actionId, 'test-actionid')
        self.assertTrue(result.errorMessage, mock_failure_text)
        self.assertFalse(result.success)
        self.assertTrue(result.type, mock_action_type)

    def test_get_action_result_info_setvlan(self):

        test_action_dict = {'customActionAttributes': [{'attributeName': 'VM_UUID', 'attributeValue': 'test-vm-uuid'}],
                            'connectorAttributes' : ''}
        test_action_obj = DeployDataHolder(test_action_dict)

        mock_deployed_app_resource_name = 'test app name'
        mock_actionid = 'test-actionid'

        result = self.connectivity_service.get_action_resource_info(deployed_app_resource_name=mock_deployed_app_resource_name,
                                                                    actionid=mock_actionid,
                                                                    action=test_action_obj)
        self.assertTrue(result.vm_uuid, 'test-vm-uuid')
        self.assertFalse(result.iface_ip)
        self.assertFalse(result.interface_port_id)
        self.assertFalse(result.interface_mac)

    def test_get_action_result_info_removevlan(self):

        test_action_dict = {'customActionAttributes': [{'attributeName': 'VM_UUID', 'attributeValue': 'test-vm-uuid'}],
                            'connectorAttributes' : [{'attributeName': 'Interface',
                                                      'attributeValue': '{"ip_address":"test_ip" , \
                                                      "mac_address": "test_mac","port_id":"test_port_id"}'}]}
        test_action_obj = DeployDataHolder(test_action_dict)

        print test_action_obj.connectorAttributes[0].attributeValue
        print jsonpickle.loads(test_action_obj.connectorAttributes[0].attributeValue)

        mock_deployed_app_resource_name = 'test app name'
        mock_actionid = 'test-actionid'

        result = self.connectivity_service.get_action_resource_info(deployed_app_resource_name=mock_deployed_app_resource_name,
                                                                    actionid=mock_actionid,
                                                                    action=test_action_obj)
        self.assertEqual(result.vm_uuid, 'test-vm-uuid')
        self.assertEqual(result.iface_ip, 'test_ip')
        self.assertEqual(result.interface_port_id, 'test_port_id')
        self.assertTrue(result.interface_mac, 'test_mac')

    def test_attach_nic_to_instance_action_result_failure(self):

        test_action_resource_info = ConnectivityActionResourceInfo(deployed_app_resource_name='test app name',
                                                                   actionid='test actionid',
                                                                   vm_uuid='test-vm-uuid',
                                                                   interface_ip='test_ip',
                                                                   interface_port_id='test_port_id',
                                                                   interface_mac='test mac')

        # self.connectivity_service.instance_service = Mock()
        self.connectivity_service.instance_service.attach_nic_to_net = Mock(return_value=None)

        result = self.connectivity_service.attach_nic_to_instance_action_result(openstack_session=self.os_session,
                                                                                action_resource_info=test_action_resource_info,
                                                                                net_id='test netid',
                                                                                logger=self.mock_logger)

        self.connectivity_service.instance_service.attach_nic_to_net.assert_called_with(openstack_session=self.os_session,
                                                                      instance_id='test-vm-uuid',
                                                                      net_id='test netid',
                                                                      logger=self.mock_logger)
        self.assertEquals(result.actionId, 'test actionid')
        self.assertEqual(result.success, 'False')

    def test_attach_nic_to_instance_action_result_success(self):

        test_action_resource_info = ConnectivityActionResourceInfo(deployed_app_resource_name='test app name',
                                                                   actionid='test actionid',
                                                                   vm_uuid='test-vm-uuid',
                                                                   interface_ip='test_ip',
                                                                   interface_port_id='test_port_id',
                                                                   interface_mac='test mac')

        # self.connectivity_service.instance_service = Mock()
        self.connectivity_service.instance_service.attach_nic_to_net = Mock(return_value=True)

        result = self.connectivity_service.attach_nic_to_instance_action_result(openstack_session=self.os_session,
                                                                                action_resource_info=test_action_resource_info,
                                                                                net_id='test netid',
                                                                                logger=self.mock_logger)

        self.connectivity_service.instance_service.attach_nic_to_net.assert_called_with(openstack_session=self.os_session,
                                                                    instance_id='test-vm-uuid',
                                                                    net_id='test netid',
                                                                    logger=self.mock_logger)
        self.assertEquals(result.actionId, 'test actionid')
        self.assertEqual(result.success, 'True')

    def test_detach_nic_from_instance_action_result_failure(self):

        test_action_resource_info = ConnectivityActionResourceInfo(deployed_app_resource_name='test app name',
                                                                   actionid='test actionid',
                                                                   vm_uuid='test-vm-uuid',
                                                                   interface_ip='test_ip',
                                                                   interface_port_id='test_port_id',
                                                                   interface_mac='test mac')

        # self.connectivity_service.instance_service = Mock()
        self.connectivity_service.instance_service.detach_nic_from_instance = Mock(return_value=None)

        result = self.connectivity_service.detach_nic_from_instance_action_result(openstack_session=self.os_session,
                                                                                  action_resource_info=test_action_resource_info,
                                                                                  net_id='test netid',
                                                                                  logger=self.mock_logger)

        self.connectivity_service.instance_service.detach_nic_from_instance.assert_called_with(
                                                                    openstack_session=self.os_session,
                                                                    instance_id='test-vm-uuid',
                                                                    port_id='test_port_id',
                                                                    logger=self.mock_logger)
        self.assertEquals(result.actionId, 'test actionid')
        self.assertEqual(result.success, 'False')

    def test_detach_nic_from_instance_action_result_success(self):

        test_action_resource_info = ConnectivityActionResourceInfo(deployed_app_resource_name='test app name',
                                                                   actionid='test actionid',
                                                                   vm_uuid='test-vm-uuid',
                                                                   interface_ip='test_ip',
                                                                   interface_port_id='test_port_id',
                                                                   interface_mac='test mac')

        # self.connectivity_service.instance_service = Mock()
        self.connectivity_service.instance_service.detach_nic_from_instance = Mock(return_value=True)

        result = self.connectivity_service.detach_nic_from_instance_action_result(openstack_session=self.os_session,
                                                                                  action_resource_info=test_action_resource_info,
                                                                                  net_id='test netid',
                                                                                  logger=self.mock_logger)

        self.connectivity_service.instance_service.detach_nic_from_instance.assert_called_with(
                                                                    openstack_session=self.os_session,
                                                                    instance_id='test-vm-uuid',
                                                                    port_id='test_port_id',
                                                                    logger=self.mock_logger)
        self.assertEquals(result.actionId, 'test actionid')
        self.assertEqual(result.success, 'True')


    def test_perform_apply_connectivity_setvlan(self):

        test_connection_request = '''{"driverRequest":{
                                        "actions":[
                                            {"type":"setVlan",
                                             "actionId":"test actionID",
                                             "actionTarget": {"fullName": "test full name"},
                                             "connectionParams" : {"vlanId" : 42}
                                             }
                                        ]}
                                    }'''

        mock_action_resource_info = Mock()
        self.connectivity_service.get_action_resource_info = Mock(return_value=mock_action_resource_info)

        self.connectivity_service.set_vlan_actions = Mock(return_value=['Success'])

        result = self.connectivity_service.perform_apply_connectivity(openstack_session=self.os_session,
                                                                      connection_request=test_connection_request,
                                                                      cp_resource_model=Mock(),
                                                                      logger=self.mock_logger)

        self.assertEqual(result.driverResponse.actionResults, ['Success'])

    def test_perform_apply_connectivity_removevlan(self):

        test_connection_request = '''{"driverRequest":{
                                        "actions":[
                                            {"type":"removeVlan",
                                             "actionId":"test actionID",
                                             "actionTarget": {"fullName": "test full name"},
                                             "connectionParams" : {"vlanId" : 42}
                                             }
                                        ]}
                                    }'''

        mock_action_resource_info = Mock()
        self.connectivity_service.get_action_resource_info = Mock(return_value=mock_action_resource_info)

        self.connectivity_service.remove_vlan_actions = Mock(return_value=['Success'])

        result = self.connectivity_service.perform_apply_connectivity(openstack_session=self.os_session,
                                                                      connection_request=test_connection_request,
                                                                      cp_resource_model=Mock(),
                                                                      logger=self.mock_logger)

        self.assertEqual(result.driverResponse.actionResults, ['Success'])
