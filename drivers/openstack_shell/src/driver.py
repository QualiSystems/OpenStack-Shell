from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface

from cloudshell.cp.openstack.openstack_shell import OpenStackShell

class OpenStackShellDriver(ResourceDriverInterface):
    def __init__(self):
        """
        ctor must be without arguments, it is created with reflection at run time
        """
        self.os_shell = OpenStackShell()
        pass

    def initialize(self, context):
        pass

    def cleanup(self):
        pass

    def deploy_from_image(self, context, request, cancellation_context):
        """
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

    def destroy_vm_only(self, context, ports):
        return self.os_shell.delete_instance(context)

    def remote_refresh_ip(self, context, ports, cancellation_context):
        return self.os_shell.refresh_ip(context)

    def get_inventory(self, context):
        return self.os_shell.get_inventory(command_context=context)
