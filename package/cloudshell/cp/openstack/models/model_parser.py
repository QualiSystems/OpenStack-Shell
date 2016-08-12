"""
A wrapper Model Parser Class OpenStackShellModelParser implementing only
static methods that return a "Model" from input Dict/Json like data.
"""

from cloudshell.cp.openstack.models.deploy_os_nova_image_instance_resource_model \
        import DeployOSNovaImageInstanceResourceModel
from cloudshell.cp.openstack.models.openstack_resource_model \
                                    import OpenStackResourceModel

class OpenStackShellModelParser(object):
    def __init__(self):
        pass

    @staticmethod
    def get_resource_model_from_context(resource):
        attrs = resource.attributes
        os_res_model = OpenStackResourceModel()
        os_res_model.controller_url = attrs['Controller URL']
        os_res_model.os_domain_name = attrs['OpenStack Domain Name']
        os_res_model.os_project_name = attrs['OpenStack Project Name']
        os_res_model.os_region = attrs['OpenStack Region']
        os_res_model.os_user_name = attrs['OpenStack User Name']
        os_res_model.os_user_password = attrs['OpenStack User Password']
        os_res_model.os_mgmt_vlan_id = attrs['OpenStack Management VLAN ID']
        os_res_model.os_mgmt_vlan_id = attrs['Quali Management VLAN ID']
        os_res_model.os_mgmt_vlan_id = attrs['OpenStack Management Subnet CIDR']
        os_res_model.os_mgmt_vlan_id = attrs['Quali Management Subnet CIDR']
        os_res_model.os_mgmt_vlan_id = attrs['OpenStack Floating IP Pool']
        return os_res_model

    @staticmethod
    def get_deploy_req_model_from_deploy_req(deploy_req):
        deploy_res_model = DeployOSNovaImageInstanceResourceModel()
        deploy_res_model.cloud_provider = deploy_req.image.cloud_provider
        # deploy_res_model.cp_avail_zone = deploy_req.image.availability_zone
        # TODO : Add other attributes
        return deploy_res_model

    @staticmethod
    def get_deploy_resource_model_from_context_resource(resource):
        attrs = resource.attributes
        deploy_resource_model = DeployOSNovaImageInstanceResourceModel()
        deploy_resource_model.cloud_provider = attrs['Cloud Provider']
        deploy_resource_model.cp_avail_zone = attrs['Availability Zone']
        deploy_resource_model.img_name = attrs['Image Name']
        deploy_resource_model.instance_flavor = attrs['Instance Flavor']
        deploy_resource_model.add_floating_ip = OpenStackShellModelParser.parse_boolean(attrs['Add Floating IP'])
        deploy_resource_model.auto_power_off = OpenStackShellModelParser.parse_boolean(attrs['Auto Power Off'])
        deploy_resource_model.auto_delete = OpenStackShellModelParser.parse_boolean(attrs['Auto Delete'])
        deploy_resource_model.autoload = OpenStackShellModelParser.parse_boolean(attrs['Autoload'])
        deploy_resource_model.inbound_ports = attrs['Inbound Ports']
        deploy_resource_model.outbound_ports = attrs['Outbound Ports']
        return deploy_resource_model

    @staticmethod
    def parse_boolean(value):
        return value.lower() in ['1', 'true']