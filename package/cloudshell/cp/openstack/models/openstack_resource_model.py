"""
Implements OpenStack CloudProvider Resource Model as a Convenience Object
"""
class OpenStackResourceModel:
    def __init__(self):
        self.controller_url = ''
        self.os_domain_name = ''
        self.os_project_name = ''
        self.os_user_name = ''
        self.os_user_password = ''
        self.qs_mgmt_os_net_uuid = ''
        self.reserved_networks = ''
        self.vlan_type = ''
        self.provider_network_interface = ''
        self.floating_ip_subnet_uuid = ''

    def __str__(self):
        desc = "OpenStack Resource: controller_url: {0}, domain: {1}, project_name : {2}, os_user_name : {3}".format(
            self.controller_url,
            self.os_domain_name,
            self.os_project_name,
            self.os_user_name)
        return desc
