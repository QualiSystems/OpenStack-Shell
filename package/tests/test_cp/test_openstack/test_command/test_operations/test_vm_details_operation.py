from unittest import TestCase

from cloudshell.cp.openstack.command.operations.vm_details_operation import VmDetailsOperation
from cloudshell.cp.openstack.domain.common.vm_details_provider import VmDetailsProvider
from mock import Mock
import cloudshell.cp.openstack.domain.services.neutron.neutron_network_service as test_neutron_network_service
from novaclient.v2.servers import NetworkInterface


class TestVmDetailsOperation(TestCase):
    def setUp(self):
        self.openstack_session = Mock()
        self.instance_service = Mock()
        self.vm_details_provider = VmDetailsProvider(self.instance_service)
        self.vm_details_operation = VmDetailsOperation(vm_details_provider=self.vm_details_provider,
                                                       instance_service=self.instance_service)

    def mock_flavor(self):
        flavor = Mock()
        flavor.name = 'Flavor Name'
        flavor.vcpus = 2
        flavor.ram = 256
        flavor.disk = 320
        return flavor

    def mock_image(self):
        image = Mock()
        image.name = 'Image Name'
        return image

    def mock_vm(self):
        vm = Mock()
        vm.name = 'OpenStack App for Tests'
        vm.image = {'id': '123'}
        vm.flavor = {'id': '456'}
        vm._info = {'OS-EXT-AZ:availability_zone': 'Av Zone'}
        vm.networks = {'network_name_for_test': ['192.168.1.1']}

        interface = Mock()
        interface.net_id = '300881'
        vm.interface_list = Mock(return_value=[interface])

        addresses = {'addresses': ''}
        vm.to_dict = Mock(return_value=addresses)

        return vm

    def test_get_vm_details(self):
        # Arrange
        image = self.mock_image()
        flavor = self.mock_flavor()
        vm = self.mock_vm()
        self.instance_service.get_instance_from_instance_id = Mock(return_value=vm)
        self.instance_service.get_image = Mock(return_value=image)
        self.instance_service.get_flavor = Mock(return_value=flavor)

        network = {'id': '300881', 'name': 'network_name_for_test', 'provider:segmentation_id': '777'}

        mock_client = Mock()
        test_neutron_network_service.neutron_client.Client = Mock(return_value=mock_client)
        mock_client.list_networks = Mock(return_value={'networks': [network]})

        param = Mock()
        param.name = 'ip_regex'
        param.value = 'bla.*'

        request = Mock()
        request.deployedAppJson.name = 'OpenStack App for Tests'
        request.deployedAppJson.vmdetails.uid = '240975'
        request.deployedAppJson.vmdetails.vmCustomParams = [param]
        request.appRequestJson.deploymentService.model = 'OpenStack'
        request.appRequestJson.deploymentService.attributes = [Mock()]

        cancellation_context = Mock(is_cancelled=False)
        management_vlan_id = Mock()

        # Act
        result = self.vm_details_operation.get_vm_details(openstack_session=self.openstack_session,
                                                          requests=[request],
                                                          cancellation_context=cancellation_context,
                                                          logger=Mock(),
                                                          management_vlan_id=management_vlan_id)

        # Assert
        self.assertEqual(len(result), 1)
        vm_details = result[0]
        self.assertEqual(next(x['value'] for x in vm_details.vm_instance_data if x['key'] == 'Image'), 'Image Name')
        self.assertEqual(next(x['value'] for x in vm_details.vm_instance_data if x['key'] == 'Flavour'), 'Flavor Name')
        self.assertEqual(next(x['value'] for x in vm_details.vm_instance_data if x['key'] == 'Availability Zone'), 'Av Zone')
        self.assertEqual(next(x['value'] for x in vm_details.vm_instance_data if x['key'] == 'Disk Size'), '320 GB')
        self.assertEqual(next(x['value'] for x in vm_details.vm_instance_data if x['key'] == 'Memory'), '256 GB')
        self.assertEqual(next(x['value'] for x in vm_details.vm_instance_data if x['key'] == 'CPU'), '2 vCPU')

        self.assertEqual(len(vm_details.vm_network_data), 1)
        nic = vm_details.vm_network_data[0]
        self.assertEqual(nic['is_predefined'], False)
        self.assertEqual(nic['network_id'], '777')

        self.assertEqual(len(nic['network_data']), 3)
        self.assertEqual(next(x['value'] for x in nic['network_data'] if x['key'] == 'IP'), '192.168.1.1')
        self.assertEqual(next(x['value'] for x in nic['network_data'] if x['key'] == 'VLAN Name'), 'network_name_for_test')
