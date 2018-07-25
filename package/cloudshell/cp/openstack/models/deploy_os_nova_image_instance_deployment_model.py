from cloudshell.cp.core.utils import *

"""
Provides a convenience Object for DeployOSNovaImageInstance Resource
"""
class DeployOSNovaImageInstanceDeploymentModel(object):
    __deploymentModel__ = 'OpenStack Deploy From Glance Image'


    def __init__(self, attributes):
        self.cloud_provider = ''
        self.availability_zone = ''
        self.image_id = ''
        self.instance_flavor = ''
        self.add_floating_ip = False
        self.autoload = False
        self.affinity_group_id = ''
        self.floating_ip_subnet_id = ''
        self.auto_udev = True


        for k,v in attributes.iteritems():
                try_set_attr(self, to_snake_case(k), v)


