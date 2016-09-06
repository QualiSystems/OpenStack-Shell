import jsonpickle

# ResourceDriverInterface and other Context utilities from shell.core
from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface
from cloudshell.shell.core.session.cloudshell_session import CloudShellSessionContext
from cloudshell.shell.core.session.logging_session import LoggingSessionContext

# From OpenStack package
from cloudshell.cp.openstack.common.deploy_data_holder import DeployDataHolder
from cloudshell.cp.openstack.models.model_parser import OpenStackShellModelParser as OSModelParser
# From Cloudshell API
from cloudshell.api.cloudshell_api import InputNameValue

class DeployOSNovaImageInstanceDriver(ResourceDriverInterface):
    APP_NAME = 'app_name'
    IMAGE_PARAM = 'image'

    def __init__(self):
        pass

    def cleanup(self):
        pass

    def initialize(self, context):
        pass

    def Deploy(self, context, Name=None):
        """
        :param cloudshell.shell.core.context.ResourceCommandContext context:
        :param str Name:
        :rtype str:
        """
        with LoggingSessionContext(context) as logger:
            with CloudShellSessionContext(context) as session:
                logger.debug("Deploy Called for Reservation: {0}".format(
                                        context.reservation.reservation_id))
                # Get CS Session we are going to make an API call using this session
                logger.debug("creating session: {0}, {1}, {2}".format(
                                context.connectivity.server_address,
                                context.connectivity.admin_auth_token,
                                context.reservation.domain))

                deploy_service_res_model = OSModelParser.get_deploy_resource_model_from_context_resource(context.resource)
                # FIXME: hacky right now
                # deploy_service_res_model.cloud_provider = 'OpenStack'

                app_name = jsonpickle.decode(context.resource.app_context.app_request_json)['name']

                deploy_req = DeployDataHolder({self.APP_NAME: app_name,
                                               self.IMAGE_PARAM: deploy_service_res_model})

                logger.debug("Calling the Shell Driver's Deploy method for app: "
                             " {0}".format(app_name))

                logger.debug("cloud_provider = {0}".format(deploy_service_res_model.cloud_provider))
                # Calls command on the OpenStack cloud provider
                result = session.ExecuteCommand(context.reservation.reservation_id,
                                                deploy_service_res_model.cloud_provider,
                                                "Resource",
                                                "deploy_from_image",
                                                self._get_command_inputs_list(deploy_req),
                                                False)
                return result.Output
                # return str(jsonpickle.encode({"vm_name": "testvm", "vm_uuid": "1234-5678",
                #                             "cloud_provider_resource_name": "openstack"},
                #                             unpicklable=False))

    def _get_command_inputs_list(self, data_holder):
        return [InputNameValue('request', jsonpickle.encode(data_holder, unpicklable=False))]
