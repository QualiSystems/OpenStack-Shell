from neutronclient.v2_0 import client as neutron_client

from cloudshell.cp.core.models import  *

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
        :return: cloudshell.cp.core.models.VmDetanoilsData
        """

        # must be reloaded to acquire a floating ip
        instance = self.instance_service.get_instance_from_instance_id(openstack_session=openstack_session,
                                                                       instance_id=instance.id,
                                                                       logger=logger)
        logger.info("Reloading vm with id: {0}".format(instance.id))

        vm_instance_data = self._get_vm_instance_data(instance, openstack_session)
        vm_network_data = self._get_vm_network_data(instance, openstack_session, management_vlan_id)

        return VmDetailsData(vmInstanceData=vm_instance_data,vmNetworkData=vm_network_data)

    def _get_vm_instance_data(self, instance, openstack_session):
        image = self.instance_service.get_image(openstack_session, instance.image['id'])
        flavor = self.instance_service.get_flavor(openstack_session, instance.flavor['id'])

        data = [
            DeployVmDataElement(key='Image',value=image.name),
            DeployVmDataElement(key='Flavour',value=flavor.name),
            DeployVmDataElement(key='Availability Zone', value=instance._info['OS-EXT-AZ:availability_zone']),
            DeployVmDataElement(key='CPU', value='%s vCPU' % flavor.vcpus),
            DeployVmDataElement(key='Memory', value='%s GB' % flavor.ram),
            DeployVmDataElement(key='Disk Size', value='%s GB' % flavor.disk)
        ]

        return data

    @staticmethod
    def _get_vm_network_data(instance, openstack_session, management_vlan_id):

        network_interfaces = []
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

            is_primary_and_predefined = network_id == management_vlan_id

            network_data = [DeployVmDataElement(key="IP",value= instance.networks[network_name][0])]

            addresses = instance.to_dict().get('addresses')
            if addresses:
                for key, val in addresses.iteritems():
                    if key == network_name:
                        floating_ip = filter(lambda x: x['OS-EXT-IPS:type'] == 'floating', val)
                        if floating_ip:
                            network_data.append(DeployVmDataElement(key="Floating IP",value= floating_ip[0]['addr']))

            network_data.append(DeployVmDataElement(key="MAC Address", value=interface_mac))
            network_data.append(DeployVmDataElement(key="VLAN Name", value=network_name,hidden=True))
            current_interface = DeployVmNetworkInterfaceDataResponse(interfaceId=interface_mac, networkId=segmentation_id,
                                                                     isPrimary=is_primary_and_predefined,
                                                                     isPredefined=is_primary_and_predefined, networkData=network_data)
            network_interfaces.append(current_interface)

        return sorted(network_interfaces, key=lambda x: x.networkId, reverse=False)
