import jsonpickle

from cloudshell.cp.openstack.command.operations.vm_details_operation import VmDetailsOperation
from cloudshell.cp.openstack.common.deploy_data_holder import DeployDataHolder
from cloudshell.cp.openstack.common.driver_helper import CloudshellDriverHelper

# Model
# from cloudshell.cp.openstack.models.deploy_os_nova_image_instance_resource_model \
#        import DeployOSNovaImageInstanceDeploymentModel
# from cloudshell.cp.openstack.models.openstack_resource_model \
#                                    import OpenStackResourceModel
from cloudshell.cp.openstack.domain.common.vm_details_provider import VmDetailsProvider
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
from cloudshell.cp.openstack.command.operations.refresh_ip_operation import RefreshIPOperation
from cloudshell.cp.openstack.command.operations.autoload_operation import AutoLoadOperation

# Command Result Parser
from cloudshell.cp.openstack.command.command_result_parser import OpenStackShellCommandResultParser

from cloudshell.cp.openstack.domain.services.session_providers.os_session_provider \
    import OpenStackSessionProvider

from cloudshell.cp.openstack.domain.services.cancellation_services.command_cancellation import \
    CommandCancellationService
from cloudshell.cp.openstack.domain.services.nova.nova_instance_service import NovaInstanceService
from cloudshell.cp.openstack.domain.services.waiters.instance import InstanceWaiter
from cloudshell.cp.openstack.domain.services.neutron.neutron_network_service import NeutronNetworkService
from cloudshell.cp.openstack.domain.services.cp_validators.cp_validator import OpenStackCPValidator
from cloudshell.cp.openstack.domain.services.connectivity.vlan_connectivity_service import VLANConnectivityService
from cloudshell.cp.core.models import *

class OpenStackShell(object):
    """
    OpenStackShell: An Object of this is created by Shell Driver. Methods of
    this class implement the functionality as required by Shell Driver, which
    provides wrapper over this class.
    """

    def __init__(self):
        self.os_session_provider = OpenStackSessionProvider()
        self.cs_driver_helper = CloudshellDriverHelper()

        # We start making user of service constructors
        self.cancellation_service = CommandCancellationService()
        self.instance_service_waiter = InstanceWaiter(cancellation_service=self.cancellation_service)
        self.instance_service = NovaInstanceService(instance_waiter=self.instance_service_waiter)
        self.vm_details_provider = VmDetailsProvider(self.instance_service)
        self.network_service = NeutronNetworkService()
        self.cp_validator_service = OpenStackCPValidator()
        self.vlan_connectivity_service = VLANConnectivityService(instance_service=self.instance_service,
                                                                 network_service=self.network_service)

        self.autoload_operation = AutoLoadOperation(cp_validator_service=self.cp_validator_service)
        self.connectivity_operation = ConnectivityOperation(connectivity_service=self.vlan_connectivity_service)
        self.deploy_operation = DeployOperation(instance_service=self.instance_service,
                                                network_service=self.network_service,
                                                cancellation_service=self.cancellation_service,
                                                vm_details_provider=self.vm_details_provider)
        self.hidden_operation = HiddenOperation(instance_service=self.instance_service,
                                                network_service=self.network_service)
        self.power_operation = PowerOperation(instance_service=self.instance_service)
        self.refresh_ip_operation = RefreshIPOperation(instance_service=self.instance_service)

        self.model_parser = OpenStackShellModelParser()
        self.command_result_parser = OpenStackShellCommandResultParser()

        self.vm_details_operation = VmDetailsOperation(self.vm_details_provider, self.instance_service)

    # ## Below all operations are implemented as public methods
    # Power Operations Begin
    def power_on(self, command_context):
        """
        Powers On the instance.
        :param cloudshell.shell.core.context.ResourceRemoteCommandContext command_context:
        :rtype None:
        """

        with LoggingSessionContext(command_context) as logger:
            with ErrorHandlingContext(logger):
                with CloudShellSessionContext(command_context) as cs_session:
                    resource_model = self.model_parser.get_resource_model_from_context(command_context.resource)

                    context_remote = command_context.remote_endpoints[0]
                    if context_remote is None:
                        raise ValueError("Cannot get remote_endpoint for command context: {0}".format(command_context))

                    deployed_app_resource = self.model_parser.deployed_app_resource_from_context_remote(context_remote)
                    deployed_app_fullname = context_remote.fullname

                    logger.debug(jsonpickle.dumps(deployed_app_resource, unpicklable=False))

                    os_session = self.os_session_provider.get_openstack_session(cs_session, resource_model, logger)
                    self.power_operation.power_on(openstack_session=os_session,
                                                  cloudshell_session=cs_session,
                                                  deployed_app_resource=deployed_app_resource,
                                                  resource_fullname=deployed_app_fullname,
                                                  logger=logger)

    def power_off(self, command_context):
        """
        Powers off the instance.
        :param cloudshell.shell.core.context.ResourceRemoteCommandContext command_context:
        :rtype None:
        """

        with LoggingSessionContext(command_context) as logger:
            with ErrorHandlingContext(logger):
                with CloudShellSessionContext(command_context) as cs_session:
                    resource_model = self.model_parser.get_resource_model_from_context(command_context.resource)

                    context_remote = command_context.remote_endpoints[0]
                    if context_remote is None:
                        raise ValueError("Cannot get remote_endpoint for command context: {0}".format(command_context))

                    deployed_app_resource = self.model_parser.deployed_app_resource_from_context_remote(context_remote)
                    deployed_app_fullname = context_remote.fullname

                    logger.info(deployed_app_resource)

                    os_session = self.os_session_provider.get_openstack_session(cs_session, resource_model, logger)
                    self.power_operation.power_off(openstack_session=os_session,
                                                   cloudshell_session=cs_session,
                                                   deployed_app_resource=deployed_app_resource,
                                                   resource_fullname=deployed_app_fullname,
                                                   logger=logger)

    # Power Operations End

    # Deploy Operations Begin

    def deploy_instance_from_image(self, command_context, deploy_app_action, cancellation_context):
        """
        Deploys an image with specification provided by deploy_request on a
        Nova instance
        :param cloudshell.shell.core.context.ResourceCommandContext command_context:
        :param cloudshell.cp.core.models.DeployApp. : Specification of for the instance to be deployed
        :param cloudshell.shell.core.context.CancellationContext cancellation_context:
        :rtype str:
        """

        with LoggingSessionContext(command_context) as logger:
            with ErrorHandlingContext(logger):
                with CloudShellSessionContext(command_context) as cs_session:



                    logger.info("Deploying: DeployAction: {0}".format(deploy_app_action))

                    # Get reservation
                    reservation_model = ReservationModel.create_reservation_model_from_context_reservation(command_context.reservation)
                    resource_model = self.model_parser.get_resource_model_from_context(command_context.resource)

                    # Obtain OpenStack Authenticated Session from cs_session, resource_model
                    # For operations to be self contained we do not 'cache' authenticated sessions
                    # Openstacks client will keep this sessions cached (or so is observed)
                    # So this does not do an API call to 'authenticate' on 'Every Command '
                    os_session = self.os_session_provider.get_openstack_session(cs_session, resource_model, logger)

                   

                    # From deploy_request obtain DeployOSNovaImageInstanceDeploymentModel


                    logger.info("Deploying: App: {0}".format(deploy_app_action.actionParams.appName))

                    # Use the authenticated session and deploy_req_model to get instance
                    deploy_action_result = self.deploy_operation.deploy(os_session=os_session,
                                                                 reservation=reservation_model,
                                                                 cp_resource_model=resource_model,
                                                                 deploy_app_action=deploy_app_action,
                                                                 cancellation_context=cancellation_context,
                                                                 logger=logger)


                    return deploy_action_result

    # Deploy Operations End

    # Hidden Operations Begin

    def delete_instance(self, command_context):
        """
        Deletes the Nova instance and associated block devices if delete_true
        is specified
        :param cloudshell.shell.core.context.ResourceRemoteCommandContext command_context:
        :rtype None:
        """
        with LoggingSessionContext(command_context) as logger:
            with ErrorHandlingContext(logger):
                with CloudShellSessionContext(command_context) as cs_session:
                    resource_model = self.model_parser.get_resource_model_from_context(command_context.resource)

                    context_remote = command_context.remote_endpoints[0]
                    if context_remote is None:
                        raise ValueError("Cannot get remote_endpoint for command context: {0}".format(command_context))

                    deployed_app_resource = self.model_parser.deployed_app_resource_from_context_remote(context_remote)
                    floating_ip = self.model_parser.get_attribute_value_by_name_ignoring_namespace(
                        context_remote.attributes, 'Public IP')

                    os_session = self.os_session_provider.get_openstack_session(cs_session, resource_model, logger)
                    self.hidden_operation.delete_instance(openstack_session=os_session,
                                                          deployed_app_resource=deployed_app_resource,
                                                          floating_ip=floating_ip,
                                                          logger=logger)

    # Hidden Operations End

    # Connectivity Operations Begin

    def refresh_ip(self, command_context):
        """
        Refresh IP
        :param cloudshell.shell.core.context.ResourceRemoteCommandContext command_context:
        :rtype None:
        """
        with LoggingSessionContext(command_context) as logger:
            with ErrorHandlingContext(logger):
                with CloudShellSessionContext(command_context) as cs_session:
                    resource_model = self.model_parser.get_resource_model_from_context(command_context.resource)

                    context_remote = command_context.remote_endpoints[0]
                    if context_remote is None:
                        raise ValueError("Cannot get remote_endpoint for command context: {0}".format(command_context))

                    deployed_app_resource = self.model_parser.deployed_app_resource_from_context_remote(context_remote)
                    deployed_app_private_ip = context_remote.address
                    deployed_app_fullname = context_remote.fullname

                    logger.info(deployed_app_resource)

                    os_session = self.os_session_provider.get_openstack_session(cs_session, resource_model, logger)
                    self.refresh_ip_operation.refresh_ip(openstack_session=os_session,
                                                         cloudshell_session=cs_session,
                                                         deployed_app_resource=deployed_app_resource,
                                                         private_ip=deployed_app_private_ip,
                                                         resource_fullname=deployed_app_fullname,
                                                         cp_resource_model=resource_model,
                                                         logger=logger)

    def apply_connectivity(self, command_context, connectivity_request):
        """

        :param cloudshell.shell.core.context.ResourceRemoteCommandContext command_context:
        :param str connectivity_request: Connectivity Request JSON string
        :return:
        """
        with LoggingSessionContext(command_context) as logger:
            with ErrorHandlingContext(logger):
                with CloudShellSessionContext(command_context) as cs_session:
                    # FIXME: When implementing a context manager create all clients inside the contextManager.
                    logger.info(connectivity_request)
                    cp_resource_model = self.model_parser.get_resource_model_from_context(command_context.resource)

                    logger.debug(cp_resource_model)
                    os_session = self.os_session_provider.get_openstack_session(cs_session, cp_resource_model, logger)
                    connectivity_results = self.connectivity_operation.apply_connectivity(openstack_session=os_session,
                                                                                         cp_resource_model=cp_resource_model,
                                                                                         conn_request=connectivity_request,
                                                                                         logger=logger)
                    return connectivity_results

    # Connectivity Operations End

    # Autoload operations Begin
    def get_inventory(self, command_context):
        """

        :param command_context:
        :return:`
        """
        with LoggingSessionContext(command_context) as logger:
            with ErrorHandlingContext(logger):
                with CloudShellSessionContext(command_context) as cs_session:
                    # FIXME: When implementing a context manager create all clients inside the contextManager.
                    cp_resource_model = self.model_parser.get_resource_model_from_context(command_context.resource)

                    logger.debug(cp_resource_model)
                    os_session = self.os_session_provider.get_openstack_session(cs_session, cp_resource_model, logger)
                    return self.autoload_operation.get_inventory(cs_session=cs_session,
                                                                 openstack_session=os_session,
                                                                 cp_resource_model=cp_resource_model,
                                                                 logger=logger)

    def get_vm_details(self, command_context, cancellation_context, requests_json):
        """Get vm details for specific deployed app

        :param requests_json:
        :param cancellation_context:
        :param command_context: ResourceRemoteCommandContext
        """
        with LoggingSessionContext(command_context) as logger:
            with ErrorHandlingContext(logger):
                with CloudShellSessionContext(command_context) as cs_session:
                    logger.info("Starting get_vm_details operation...")

                    requests = DeployDataHolder(jsonpickle.decode(requests_json)).items
                    cp_resource_model = self.model_parser.get_resource_model_from_context(command_context.resource)

                    logger.debug(cp_resource_model)
                    management_vlan_id = cp_resource_model.qs_mgmt_os_net_uuid

                    os_session = self.os_session_provider.get_openstack_session(cs_session, cp_resource_model, logger)
                    vm_details = self.vm_details_operation.get_vm_details(openstack_session=os_session,
                                                                          requests=requests,
                                                                          cancellation_context=cancellation_context,
                                                                          logger=logger,
                                                                          management_vlan_id=management_vlan_id)
                    return self.command_result_parser.set_command_result(vm_details)
