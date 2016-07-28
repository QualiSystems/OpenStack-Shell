"""
Implements OpenStack CloudProvider Resource Model as a Convenience Object
"""
class OpenStackResourceModel:
    def __init__(self):
        self.controller_url = ''
        self.domain = ''
        self.project_name = ''
        self.os_user_name = ''
        self.os_user_password = ''
        self.os_mgmt_vlan_id = ''
        self.qs_mgmt_vlan_id = ''

