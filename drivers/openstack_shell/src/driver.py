from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface


class OpenStackShellDriver(ResourceDriverInterface):
    def cleanup(self):
        pass

    def __init__(self):
        """
        ctor must be without arguments, it is created with reflection at run time
        """
        pass

    def initialize(self, context):
        pass

    def deploy_from_image(self, context, request):
        return str(jsonpickle.encode({"vm_name": "testvm", "vm_uuid": "1234-5678",
                                    "cloud_provider_resource_name" : "openstack"},
                                    unpicklable=False))

    def power_on(self, context, ports):
        return str(jsonpickle.encode(True, unpicklable=False))

    def power_off(self, context, ports):
        return str(jsonpickle.encode(True, unpicklable=False))
