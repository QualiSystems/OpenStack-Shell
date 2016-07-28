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
    def get_resource_model_from_context(context):
        return OpenStackResourceModel()
        pass

    @staticmethod
    def get_deploy_req_model_from_deploy_req(deploy_req):
        return DeployOSNovaImageInstanceResourceModel()

