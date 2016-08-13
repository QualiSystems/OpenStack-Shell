"""
Implements OpenStack CloudProvider Resource Model as a Convenience Object
"""
class OpenStackResourceModel:
    def __init__(self):
        self.controller_url = ''
        self.os_domain_name = ''
        self.os_project_name = ''
        self.os_region = ''
        self.os_user_name = ''
        self.os_user_password = ''
        self.os_mgmt_vlan_id = ''
        self.qs_mgmt_vlan_id = ''
        self.os_mgmt_subnet_cidr = ''
        self.qs_mgmt_subnet_cidr = ''
        self.os_floating_ip_pool = ''

    def __str__(self):
        desc = "OpenStack Resource: controller_url: {0}, domain: {1}, project_name : {2}, os_user_name : {3}".format(
            self.controller_url,
            self.os_domain_name,
            self.os_project_name,
            self.os_user_name)
        return desc
