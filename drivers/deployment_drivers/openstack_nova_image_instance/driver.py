import jsonpickle

# ResourceDriverInterface and other Context utilities from shell.core
from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface
from cloudshell.shell.core.session.cloudshell_session import CloudShellSessionContext
from cloudshell.shell.core.session.logging_session import LoggingSessionContext
from cloudshell.core.context.error_handling_context import ErrorHandlingContext

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
            with ErrorHandlingContext(logger):
                with CloudShellSessionContext(context) as session:
                    logger.info("Deploy Called for Reservation: {0}".format(context.reservation.reservation_id))
                    # Get CS Session we are going to make an API call using this session
                    logger.info("creating session: {0}, {1}, {2}".format(context.connectivity.server_address,
                                                                          context.connectivity.admin_auth_token,
                                                                          context.reservation.domain))

                    deploy_service_res_model = OSModelParser.get_deploy_resource_model_from_context_resource(context.resource)

                    context_json_decoded = jsonpickle.decode(context.resource.app_context.app_request_json)

                    app_name = context_json_decoded['name']
                    cloud_provider_name = context_json_decoded["deploymentService"].get("cloudProviderName")

                    logger.info("cloud_provider_name from context = {0}".format(cloud_provider_name))

                    if cloud_provider_name:
                        deploy_service_res_model.cloud_provider = str(cloud_provider_name)

                    deploy_req = DeployDataHolder({self.APP_NAME: app_name,
                                                   self.IMAGE_PARAM: deploy_service_res_model})

                    logger.info("Calling the Shell Driver's Deploy method for app: {0}".format(app_name))

                    logger.info("cloud_provider = {0}".format(deploy_service_res_model.cloud_provider))
                    # Calls command on the OpenStack cloud provider
                    result = session.ExecuteCommand(context.reservation.reservation_id,
                                                    deploy_service_res_model.cloud_provider,
                                                    "Resource",
                                                    "deploy_from_image",
                                                    self._get_command_inputs_list(deploy_req),
                                                    False)
                    return result.Output

    def _get_command_inputs_list(self, data_holder):
        return [InputNameValue('request', jsonpickle.encode(data_holder, unpicklable=False))]
