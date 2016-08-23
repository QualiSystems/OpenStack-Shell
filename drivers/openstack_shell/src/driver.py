from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface

from cloudshell.cp.openstack.openstack_shell import OpenStackShell
import jsonpickle


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

    def deploy_from_image(self, context, request):
        """
        :param context:
        :type context:
        :param request:
        :type request:
        :return:
        :rtype  : str
        """
        return self.os_shell.deploy_instance_from_image(context, request)
        #return str(jsonpickle.encode({"vm_name": "testvm_shell_driver", "vm_uuid": "1234-5678",
        #                           "cloud_provider_resource_name" : "openstack"},
        #                            unpicklable=False))

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

