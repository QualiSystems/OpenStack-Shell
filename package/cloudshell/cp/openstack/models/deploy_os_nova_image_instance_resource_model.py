"""
Provides a convenience Object for DeployOSNovaImageInstance Resource
"""
class DeployOSNovaImageInstanceResourceModel(object):
    def __init__(self):
        self.cloud_provider = ''
        self.cp_region = ''
        self.cp_avail_zone = ''
        self.img_name = ''
        self.instance_flavor = ''
        self.add_floating_ip = False
        self.floating_ip = ''
        self.auto_power_off = False
        self.autoload = False
        self.auto_delete = False
        self.outbound_ports = ''
        self.inbound_ports = ''
