class ConnectivityActionResourceInfo:
    def __init__(self, deployed_app_resource_name, actionid, vm_uuid, interface_ip, interface_port_id, interface_mac):
        self.deployed_app_resource_name = deployed_app_resource_name
        self.vm_uuid = vm_uuid
        self.actionid = actionid
        self.iface_ip = interface_ip
        self.interface_port_id = interface_port_id
        self.interface_mac = interface_mac

    def __str__(self):
        return "deployed_app_resource_name: {0}, vm_uuid: {1}, actionid: {2}, iface_ip: {3}, interface_port_id: {4}, " \
               "interface_mac: {5}".format(self.deployed_app_resource_name, self.vm_uuid, self.actionid, self.iface_ip,
                                           self.interface_port_id, self.interface_mac)
