"""
Provides a convenience Object for DeployOSNovaImageInstance Resource
"""
class DeployOSNovaImageInstanceResourceModel(object):
    def __init__(self):
        self.cloud_provider = ''
        self.cp_avail_zone = ''
        self.img_uuid = ''
        self.instance_flavor = ''
        self.add_floating_ip = False
        self.autoload = False
        self.outbound_ports = ''
        self.inbound_ports = ''
