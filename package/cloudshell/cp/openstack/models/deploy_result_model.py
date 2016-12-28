class DeployResultModel(object):
    def __init__(self, vm_name, vm_uuid, cloud_provider_name, deployed_app_ip, deployed_app_attributes,
                 floating_ip):

        self.vm_name = vm_name
        self.vm_uuid = vm_uuid
        self.cloud_provider_resource_name = cloud_provider_name
        #self.autoload = autoload
        #self.auto_delete = autodelete
        self.wait_for_ip = False
        #self.auto_power_off = auto_power_off
        self.deployed_app_attributes = deployed_app_attributes
        self.deployed_app_address = deployed_app_ip
        self.default_sec_group_uuid = ''
        self.floating_ip = floating_ip
