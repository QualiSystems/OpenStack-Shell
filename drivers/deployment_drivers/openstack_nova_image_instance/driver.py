from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface
import jsonpickle

class DeployOSNovaImageInstance(ResourceDriverInterface):

    def __init__(self):
        pass # Empty right now

    def cleanup(self):
        pass

    def initialize(self, context):
        pass # TODO : Figure out what is to be done next?

    def Deploy(self, context, Name=None):
        # FIXME: Just copy pasting hard-coded deploy_ami output.
        return str(jsonpickle.encode({"vm_name": "testvm", "vm_uuid": "1234-5678",
                                    "cloud_provider_resource_name" : "openstack"},
                                    unpicklable=False))

