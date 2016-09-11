"""
A wrapper Model Parser Class OpenStackShellModelParser implementing only
static methods that return a "Model" from input Dict/Json like data.
"""

from cloudshell.cp.openstack.models.deploy_os_nova_image_instance_resource_model \
        import DeployOSNovaImageInstanceResourceModel
from cloudshell.cp.openstack.models.openstack_resource_model import OpenStackResourceModel
from cloudshell.cp.openstack.common.deploy_data_holder import DeployDataHolder
import jsonpickle

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
        os_res_model.qs_mgmt_os_net_uuid = attrs['Quali Management Network UUID']
        os_res_model.os_floating_ip_pool = attrs['Floating IP Pool']
        return os_res_model

    @staticmethod
    def deploy_res_model_appname_from_deploy_req(deploy_req):
        data = jsonpickle.decode(deploy_req)
        data_holder = DeployDataHolder(data)
        deploy_res_model = DeployOSNovaImageInstanceResourceModel()
        deploy_res_model.cloud_provider = data_holder.image.cloud_provider
        deploy_res_model.cp_avail_zone = data_holder.image.cp_avail_zone
        deploy_res_model.img_name = data_holder.image.img_name
        deploy_res_model.instance_flavor = data_holder.image.instance_flavor
        deploy_res_model.add_floating_ip = data_holder.image.add_floating_ip
        deploy_res_model.autoload = data_holder.image.autoload
        deploy_res_model.inbound_ports = data_holder.image.inbound_ports
        deploy_res_model.outbound_ports = data_holder.image.outbound_ports

        app_name = data_holder.app_name

        return deploy_res_model, app_name

    @staticmethod
    def get_deploy_resource_model_from_context_resource(resource):
        attrs = resource.attributes
        deploy_resource_model = DeployOSNovaImageInstanceResourceModel()
        deploy_resource_model.cloud_provider = attrs['Cloud Provider']
        deploy_resource_model.cp_avail_zone = attrs['Availability Zone']
        deploy_resource_model.img_name = attrs['Image Name']
        deploy_resource_model.instance_flavor = attrs['Instance Flavor']
        deploy_resource_model.add_floating_ip = OpenStackShellModelParser.parse_boolean(attrs['Add Floating IP'])
        deploy_resource_model.autoload = OpenStackShellModelParser.parse_boolean(attrs['Autoload'])
        deploy_resource_model.inbound_ports = attrs['Inbound Ports']
        deploy_resource_model.outbound_ports = attrs['Outbound Ports']
        return deploy_resource_model


    @staticmethod
    def parse_boolean(value):
        return value.lower() in ['1', 'true']

    @staticmethod
    def deployed_app_resource_from_context_remote(context_remote):
        deployed_app_json = jsonpickle.decode(context_remote.app_context.deployed_app_json)
        return DeployDataHolder(deployed_app_json)