from cloudshell.cp.openstack.common.driver_helper import CloudshellDriverHelper

# Model
# from cloudshell.cp.openstack.models.deploy_os_nova_image_instance_resource_model \
#        import DeployOSNovaImageInstanceResourceModel
# from cloudshell.cp.openstack.models.openstack_resource_model \
#                                    import OpenStackResourceModel
from cloudshell.cp.openstack.models.reservation_model import ReservationModel
# Model Parser
from cloudshell.cp.openstack.models.model_parser import OpenStackShellModelParser

# New shell-core contexts
from cloudshell.shell.core.session.cloudshell_session import CloudShellSessionContext
from cloudshell.shell.core.session.logging_session import LoggingSessionContext
from cloudshell.core.context.error_handling_context import ErrorHandlingContext
# Command Operations
from cloudshell.cp.openstack.command.operations.power_operation import PowerOperation
from cloudshell.cp.openstack.command.operations.deploy_operation import DeployOperation
from cloudshell.cp.openstack.command.operations.connectivity_operation import ConnectivityOperation
from cloudshell.cp.openstack.command.operations.hidden_operation import HiddenOperation

# Command Result Parser
from cloudshell.cp.openstack.command.command_result_parser import OpenStackShellCommandResultParser

# Instance Services

from cloudshell.cp.openstack.domain.services.session_providers.os_session_provider \
                                            import OpenStackSessionProvider

class OpenStackShell(object):
    """
    OpenStackShell: An Object of this is created by Shell Driver. Methods of
    this class implement the functionality as required by Shell Driver, which
    provides wrapper over this class.
    """
    def __init__(self):
        self.os_session_provider = OpenStackSessionProvider()
        self.cs_driver_helper = CloudshellDriverHelper()

        self.power_operation = PowerOperation()
        self.deploy_operation = DeployOperation()
        self.connectivity_operation = ConnectivityOperation()
        self.hidden_operation = HiddenOperation()

        self.model_parser = OpenStackShellModelParser()
        self.command_result_parser = OpenStackShellCommandResultParser()

    ### Below all operations are implemented as public methods
    ## Power Operations Begin
    def power_on(self, command_context):
        """
        Powers On the instance.
        :param command_context:
        :type command_context:
        :return None
        """

        with LoggingSessionContext(command_context) as logger:
            with ErrorHandlingContext(logger):
                with CloudShellSessionContext(command_context) as cs_session:
                    # FIXME: Add details
                    self.power_operation.power_on()

    def power_off(self, command_context):
        """
        Powers off the instance.
        :param command_context:
        :type command_context:
        :return None:
        """
        with LoggingSessionContext(command_context) as logger:
            with ErrorHandlingContext(logger):
                with CloudShellSessionContext(command_context) as cs_session:
                    # FIXME: Add details
                    self.power_operation.power_off()
    ## Power Operations Begin

    ## Deploy Operations Begin
    def deploy_instance(self, command_context, deploy_request):
        """
        Deploys an image with specification provided by deploy_request on a
        Nova instance
        :param command_context:
        :type command_context:
        :param deploy_request: Specification of for the instance to be dployed
        :return :
        :rtype :
        """

        with LoggingSessionContext(command_context) as logger:
            with ErrorHandlingContext(logger):
                with CloudShellSessionContext(command_context) as cs_session:
                    resource_model = self.model_parser.get_resource_model_from_context(command_context.resource)

                    # Obtain OpenStack Authenticated Session from cs_session, resource_model
                    # For operations to be self contained we do not 'cache' authenticated sessions
                    # Openstacks client will keep this sessions cached (or so is observed)
                    # So this does not do an API call to 'authenticate' on 'Every Command '
                    os_session = self.os_session_provider.get_openstack_session(cs_session, resource_model)

                    # Get App name 'to be passed to instance creation'
                    app_name = deploy_request.app_name

                    # Get reservation
                    reservation_model = ReservationModel.create_reservation_model_from_context_reservation(
                                                                                            command_context.reservation)
                    # From deploy_request obtain DeployOSNovaImageInstanceResourceModel
                    deploy_req_model = self.model_parser.get_deploy_req_model_from_deploy_req(deploy_request)

                    # Use the authenticated session and deploy_req_model to get instance
                    # FIXME: Add, error - can be used in 'what' of Exception
                    deployed_data, error = self.deploy_operation.deploy(os_session=os_session,
                                                                        name=app_name,
                                                                        reservation=reservation_model,
                                                                        deploy_req_model=deploy_req_model)

                    if not deployed_data:
                        # Raise an exception that instance creation failed
                        raise Exception("Failed to Deploy App: Instance creation failed {0}".format(error))

                    return self.command_result_parser.set_command_result(deployed_data)
    ## Deploy Operations End

    ## Hidden Operations Begin
    def delete_instance(self, command_context):
        """
        Deletes the Nova instance and associated block devices if delete_true
        is specified
        :param command_context:
        :type command_context:
        :return :
        :rtype :
        """
        with LoggingSessionContext(command_context) as logger:
            with ErrorHandlingContext(logger):
                with CloudShellSessionContext(command_context) as cs_session:
                    resource_model = self.model_parser.get_resource_model_from_context(command_context.resource)

                    # FIXME: Add details
                    self.hidden_operation.delete_instance()

    ## Hidden Operations End

    ## Connectivity Operations Begin
    def refresh_ip(self, command_context):
        """
        Refresh IP
        :param command_context:
        :type command_context:
        :return :
        :rtype :
        """
        with LoggingSessionContext(command_context) as logger:
            with ErrorHandlingContext(logger):
                with CloudShellSessionContext(command_context) as cs_session:

                    # FIXME: Add details
                    self.connectivity_operation.refresh_ip()

    ## Connectivity Operations Begin


    ## All private methods End
