import jsonpickle

# The ResourceDriverInterface
from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface

# Logger
from cloudshell.core.logger.qs_logger import get_qs_logger

# From OpenStack package
from cloudshell.cp.openstack.common.driver_helper import CloudshellDriverHelper
from cloudshell.cp.openstack.common.deploy_data_holder import DeployDataHolder
from cloudshell.cp.openstack.models.deploy_os_nova_image_instance_resource_model \
                            import DeployOSNovaImageInstanceResourceModel

class DeployOSNovaImageInstanceDriver(ResourceDriverInterface):

    CAT_NAME = "OpenStackCloudShell"
    CLASS_NAME = 'DeployOSNovaImageInstanceDriver'
    APP_NAME = 'app_name'
    IMAGE_PARAMS = 'img_params'

    def __init__(self):
        # FIXME: Right now there's CloudShellDriverHelper is there in
        #        each of 'cloud-shells' a better place is 'cloudshell.core'?
        self.cs_helper = CloudshellDriverHelper()
        self.logger = None

    def cleanup(self):
        pass

    def initialize(self, context):
        #reservation_id = context.reservation.reservation_id
        log_group = self.CLASS_NAME
	log_cat = self.CAT_NAME

        self.logger = get_qs_logger(log_category=log_cat,
                                    log_group=log_group)

    def Deploy(self, context, Name=None):
        """
        :param context: reservation context
        :type context:
        """

        self.logger.debug("Deploy Called for Reservation : %(res_id)s:" %
                            {'res_id' : context.reservation.reservation_id})
        # Get CS Session we are going to make an API call using this session
        self.logger.debug("creating sessionx: %(server)s, %(token)s, %(domain)s"
                            % { 'server': context.connectivity.server_address,
                                'token': context.connectivity.admin_auth_token,
                                'domain': context.reservation.domain})
        session = self.cs_helper.get_session(context.connectivity.server_address,
                                        context.connectivity.admin_auth_token,
                                        context.reservation.domain)

        deploy_service_res_model = DeployOSNovaImageInstanceResourceModel()

        app_name = jsonpickle.decode(
                        context.resource.app_context.app_request_json)['name']

        deploy_req = DeployDataHolder({self.APP_NAME: app_name,
                                       self.IMAGE_PARAMS : deploy_service_res_model})

        self.logger.debug("Calling the Shell Driver's Deploy method for app: " \
                            " %(name)s" % {'name':app_name})

        return str(jsonpickle.encode({"vm_name": "testvm", "vm_uuid": "1234-5678",
                                    "cloud_provider_resource_name" : "openstack"},
                                    unpicklable=False))

