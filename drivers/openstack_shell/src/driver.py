import jsonpickle
from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface

from cloudshell.cp.openstack.openstack_shell import OpenStackShell


class OpenStackShellDriver(ResourceDriverInterface):
    def __init__(self):
        """
        ctor must be without arguments, it is created with reflection at run time
        """
        self.deployments = dict()
        self.deployments['OpenStack Deploy From Glance Image'] = self.deploy_from_image
        self.os_shell = OpenStackShell()

    def Deploy(self, context, request=None, cancellation_context=None):
        """
        :param cloudshell.shell.core.context.ResourceCommandContext context:
        :param DeployDataHolder request:
        :param cloudshell.shell.core.context.CancellationContext cancellation_context:
        :return:
        """
        app_request = jsonpickle.decode(request)
        deployment_name = app_request['DeploymentServiceName']

        if deployment_name in self.deployments.keys():
            return self.deployments[deployment_name](context, request, cancellation_context)
        else:
            raise Exception('Could not find the deployment')

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
        return self.os_shell.deploy_instance_from_image(command_context=context, deploy_request=request,
                                                        cancellation_context=cancellation_context)

    def ApplyConnectivityChanges(self, context, request):
        return self.os_shell.apply_connectivity(context, request)

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
