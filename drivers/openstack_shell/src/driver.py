from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface

from cloudshell.cp.openstack.models.deploy_os_nova_image_instance_deployment_model import \
    DeployOSNovaImageInstanceDeploymentModel
from cloudshell.cp.openstack.openstack_shell import OpenStackShell

from cloudshell.cp.core import DriverRequestParser
from cloudshell.cp.core.models import *
from cloudshell.cp.core.utils import *


class OpenStackShellDriver(ResourceDriverInterface):
    def __init__(self):
        """
        ctor must be without arguments, it is created with reflection at run time
        """
        self.deployments = dict()
        self.parser = DriverRequestParser()
        self.parser.add_deployment_model(DeployOSNovaImageInstanceDeploymentModel)
        self.deployments[DeployOSNovaImageInstanceDeploymentModel.__deploymentModel__] = self.deploy_from_image
        self.os_shell = OpenStackShell()

    def Deploy(self, context, request=None, cancellation_context=None):
        """
        :param cloudshell.shell.core.context.ResourceCommandContext context:
        :param DeployDataHolder request:
        :param cloudshell.shell.core.context.CancellationContext cancellation_context:
        :return:
        """
        actions = self.parser.convert_driver_request_to_actions(request)
        deploy_action =   single(actions,lambda x: isinstance(x,DeployApp))
        deployment_path = deploy_action.actionParams.deployment.deploymentPath

        if not deployment_path in self.deployments.keys():
            raise Exception('Could not find deployment')

        deploy_action_result = self.deployments[deployment_path](context, deploy_action, cancellation_context)
        driver_response = DriverResponse([deploy_action_result])

        return driver_response.to_driver_response_json()


    def initialize(self, context):
        pass

    def cleanup(self):
        pass

    def deploy_from_image(self, context, request, cancellation_context):
        """
        :param cloudshell.shell.core.context.CancellationContext cancellation_context:
        :param cloudshell.shell.core.context.ResourceCommandContext context:
        :param DeployDataHolder request:
        :rtype  : str
        """
        deploy_action_result = self.os_shell.deploy_instance_from_image(command_context=context,deploy_app_action =request,
                                                        cancellation_context=cancellation_context)

        return deploy_action_result

    def ApplyConnectivityChanges(self, context, request):
        apply_connectivity_results =  self.os_shell.apply_connectivity(context, request)
        driver_response = DriverResponse(apply_connectivity_results)

        return driver_response.to_driver_response_json()

    def PowerOn(self, context, ports):
        return self.os_shell.power_on(context)

    def PowerOff(self, context, ports):
        return self.os_shell.power_off(context)

    def PowerCycle(self, context, ports, delay):
        pass

    def DeleteInstance(self, context, ports):
        return self.os_shell.delete_instance(context)

    def remote_refresh_ip(self, context, ports, cancellation_context):
        return self.os_shell.refresh_ip(context)

    def get_inventory(self, context):
        return self.os_shell.get_inventory(command_context=context)

    def GetVmDetails(self, context, cancellation_context, requests):
        return self.os_shell.get_vm_details(context, cancellation_context, requests)
