from cloudshell.cp.openstack.common.deploy_data_holder import DeployDataHolder
from neutronclient.v2_0 import client as neutron_client


class VmDetailsProvider(object):
    def __init__(self, instance_service):
        """
        :param NovaInstanceService instance_service:
        """
        self.instance_service = instance_service

    def create(self, instance, openstack_session, management_vlan_id, logger):
        """
        :param logger:
        :param management_vlan_id:
        :param instance:
        :param keystoneauth1.session.Session openstack_session:
        :return:
        """

        # must be reloaded to acquire a floating ip
        instance = self.instance_service.get_instance_from_instance_id(openstack_session=openstack_session,
                                                                       instance_id=instance.id,
                                                                       logger=logger)
        logger.info("Reloading vm with id: {0}".format(instance.id))

        vm_details = VmDetails(instance.name)

        vm_details.vm_instance_data = self._get_vm_instance_data(instance, openstack_session)
        vm_details.vm_network_data = self._get_vm_network_data(instance, openstack_session, management_vlan_id, logger)

        return vm_details

    def _get_vm_instance_data(self, instance, openstack_session):
        image = self.instance_service.get_image(openstack_session, instance.image['id'])
        flavor = self.instance_service.get_flavor(openstack_session, instance.flavor['id'])

        data = [
            AdditionalData('Image', image.name),
            AdditionalData('Flavour', flavor.name),
            AdditionalData('Availability Zone', instance._info['OS-EXT-AZ:availability_zone']),
            AdditionalData('CPU', '%s vCPU' % flavor.vcpus),
            AdditionalData('Memory', '%s GB' % flavor.ram),
            AdditionalData('Disk Size', '%s GB' % flavor.disk)
        ]
        return data

    @staticmethod
    def _get_vm_network_data(instance, openstack_session, management_vlan_id, logger):
        network_interface_objects = []

        client = neutron_client.Client(session=openstack_session, insecure=True)
        list_networks = client.list_networks()
        networks = list_networks['networks']

        for network_name in instance.networks:
            interfaces = instance.interface_list()
            net = filter(lambda x: x['name'] == network_name, networks)[0]
            network_id = net['id']
            segmentation_id = net['provider:segmentation_id']
            interface = filter(lambda x: x.net_id == network_id, interfaces)[0]
            interface_mac = interface.to_dict().get('mac_addr')

            network_interface_object = {
                "interface_id": interface_mac,
                "network_id": segmentation_id,
                "network_data": [AdditionalData("IP", instance.networks[network_name][0])],
                "is_predefined": network_id == management_vlan_id,
                "is_primary": network_id == management_vlan_id
            }

            addresses = instance.to_dict().get('addresses')
            if addresses:
                for key, val in addresses.iteritems():
                    if key == network_name:
                        floating_ip = filter(lambda x: x['OS-EXT-IPS:type'] == 'floating', val)
                        if floating_ip:
                            network_interface_object["network_data"].append(
                                AdditionalData("Floating IP", floating_ip[0]['addr']))

            network_interface_object["network_data"].append(AdditionalData("MAC Address", interface_mac))
            network_interface_object["network_data"].append(AdditionalData("VLAN Name", network_name, True))

            network_interface_objects.append(network_interface_object)

        return sorted(network_interface_objects, key=lambda x: x['network_id'], reverse=False)


class VmDetails(object):
    def __init__(self, app_name):
        self.app_name = app_name
        self.error = None
        self.vm_instance_data = {}  # type: dict
        self.vm_network_data = []  # type: list[VmNetworkData]


class VmNetworkData(object):
    def __init__(self):
        self.interface_id = {}  # type: str
        self.network_id = {}  # type: str
        self.is_primary = False  # type: bool
        self.network_data = {}  # type: dict


def AdditionalData(key, value, hidden=False):
    """
    :type key: str
    :type value: str
    :type hidden: bool
    """
    return {
        "key": key,
        "value": value,
        "hidden": hidden
    }
