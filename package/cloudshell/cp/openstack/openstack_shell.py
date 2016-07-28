from cloudshell.cp.openstack.common.driver_helper import CloudshellDriverHelper

# Model
from cloudshell.cp.openstack.models.deploy_os_nova_image_instance_resource_model \
        import DeployOSNovaImageInstanceResourceModel
from cloudshell.cp.openstack.models.openstack_resource_model \
                                    import OpenStackResourceModel

# Model Parser
from cloudshell.cp.openstack.models.model_parser import OpenStackShellModelParser

# Command Operations
from cloudshell.cp.openstack.command.operations.power_operation \
                            import PowerOperation
from cloudshell.cp.openstack.command.operations.deploy_operation \
                            import DeployOperation
from cloudshell.cp.openstack.command.operations.connectivity_operation \
                            import ConnectivityOperation
from cloudshell.cp.openstack.command.operations.hidden_operation \
                            import HiddenOperation

# Command Result Parser
from cloudshell.cp.openstack.command.command_result_parser \
                                import OpenStackShellCommandResultParser

# Instance Services

from cloudshell.cp.openstack.domain.services.session_providers.os_session_provider \
                                            import OpenStackSessionProvider
#from cloudshell.cp.openstack.domain.services.nova.nova_instance_service \
                                            #import NovaInstanceService
#from cloudshell.cp.openstack.domain.services.neutron.neutron_network_service \
                                            #import NeutroNetworkService

# Our Exceptions # FIXME: Derive from some Quali Standard Exception Class?
class OpenStackShellPowerOnException(Exception):
    pass

class OpenStackShellPowerOffException(Exception):
    pass

class OpenStackShellDeployException(Exception):
    pass

class OpenStackShellDeleteException(Exception):
    pass

class OpenStackShellRefreshIPException(Exception):
    pass

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

        # services that we'd be using
        #self.instance_service = NovaInstanceService()
        #self.neutron_service = NeutronInstanceService()
        #self.cinder_service = CinderVolumeService()

        # FIXME: get our own logger.

    ### Below all operations are implemented as public methods
    ## Power Operations Begin
    def power_on(self, context):
        """
        Powers On the instance.
        :param context:
        :type context:
        :return None
        """
        cs_session, resource_model = \
                    self._get_cs_session_and_resource_model(context)

        os_session = self.os_session_provider.\
                            get_session(cs_session, resource_model)
        # FIXME: Add details
        self.power_operation.power_on()

    def power_off(self, context):
        """
        Powers off the instance.
        :param context:
        :type context:
        :return None:
        """
        cs_session, resource_model = \
                    self._get_cs_session_and_resource_model(context)

        os_session = self.os_session_provider.\
                            get_session(cs_session, resource_model)
        # FIXME: Add details
        self.power_operation.power_off()

    ## Power Operations Begin

    ## Deploy Operations Begin
    def deploy_instance(self, context, deploy_request):
        """
        Deploys an image with specification provided by deploy_request on a
        Nova instance
        :param context:
        :type context:
        :param deploy_request: Specification of for the instance to be dployed
        :return :
        """

        # Obtain OpenStack Authenticated Session from cs_session, resource_model
        cs_session, resource_model = \
                    self._get_cs_session_and_resource_model(context)

        # For operations to be self contained we do not 'cache' authenticated sessions
        # Openstacks client will keep this sessions cached (or so is observed)
        # So this does not do an API call to 'authenticate' on 'Every Command '
        os_session = self.os_session_provider.\
                            get_session(cs_session, resource_model)

        # Get App name 'to be passed to instance creation'

        # Get reservation

        # From deploy_request obtain DeployOSNovaImageInstanceResourceModel
        deploy_req_model = self.model_parser.\
                            get_deploy_req_model_from_deploy_req(deploy_req)

        # Use the authenticated session and deploy_req_model to get instance
        # FIXME: Add, error - can be used in 'what' of Exception
        deployed_data, error = self.deploy_operation.deploy(os_session, name,
                                                reservation, deploy_req_model)

        if not deployed_data:
            # Raise an exception that instance creation failed
            # FIXME: return "error"
            raise OpenStackDeployException("Failed to Deploy App: \
                                            Instance creation failed")

        return self.command_result_parser.set_command_result(deployed_data)

    ## Deploy Operations End

    ## Hidden Operations Begin
    def delete_instance(self, context):
        """
        Deletes the Nova instance and associated block devices if delete_true
        is specified
        :param context:
        :type context:
        :return :
        """
        cs_session, resource_model = \
                    self._get_cs_session_and_resource_model(context)

        os_session = self.os_session_provider.\
                            get_session(cs_session, resource_model)
        # FIXME: Add details
        self.hidden_operation.delete_instance()
        pass

    ## Hidden Operations End

    ## Connectivity Operations Begin
    def refresh_ip(self, context):
        cs_session, resource_model = \
                    self._get_cs_session_and_resource_model(context)

        os_session = self.os_session_provider.\
                            get_session(cs_session, resource_model)
        # FIXME: Add details
        self.connectivity_operation.refresh_ip()

    ## Connectivity Operations Begin

    ## All private methods Begin
    def _get_cs_session_and_resource_model(self, context):
        """
        A helper function that obtains Cloudshell Session and Resource Model
        Objects. Required by almost all commands.
        :param context:
        :type context:
        """
        cs_session = self.cs_driver_helper.\
                            get_session(context.connectivity.server_address,
                                        context.connectivity.admin_auth_token,
                                        context.reservation.domain)

        resource_model = self.model_parser.\
                            get_resource_model_from_context(context.resource)

        return cs_session, resource_model

    ## All private methods End
