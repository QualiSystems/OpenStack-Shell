from unittest import TestCase
import jsonpickle
from mock import Mock, patch

from cloudshell.cp.openstack.openstack_shell import OpenStackShell
from cloudshell.cp.openstack.models.openstack_resource_model import OpenStackResourceModel
from cloudshell.cp.openstack.models.deploy_os_nova_image_instance_deployment_model import DeployOSNovaImageInstanceDeploymentModel
from cloudshell.cp.openstack.models.deploy_result_model import DeployResultModel
from cloudshell.cp.core.models import *
from cloudshell.cp.core.converters import *

class TestOpenStackShell(TestCase):

    def setUp(self):
        self.os_shell_api = OpenStackShell()

        # We will need to send command_context for every method almost, so better setup here
        self.command_context = Mock()
        self.command_context.resource = Mock()
        self.command_context.remote_endpoints = []

        self.command_context.connectivity = Mock()
        self.command_context.connectivity.server_address = Mock()
        self.command_context.connectivity.admin_auth_token = Mock()

        self.command_context.reservation = Mock()
        self.command_context.reservation.domain = Mock()

        self.command_context.remote_reservation = Mock()
        self.command_context.remote_reservation.domain = Mock()
        self.os_shell_api.model_parser.get_resource_model_from_context = Mock(return_value=OpenStackResourceModel)
        self.os_shell_api.os_session_provider.get_openstack_session = Mock(return_value=Mock())

    @patch('cloudshell.cp.openstack.openstack_shell.jsonpickle.dumps')
    def test_power_on(self, json_dumps):
        """

        :return:
        """
        mock_logger = Mock()
        with patch('cloudshell.cp.openstack.openstack_shell.LoggingSessionContext', autospec=True) as mock_logger:
            with patch('cloudshell.cp.openstack.openstack_shell.ErrorHandlingContext'):
                with patch('cloudshell.cp.openstack.openstack_shell.CloudShellSessionContext') as mock_cs_session:

                    mock_cs_session_obj = Mock()
                    mock_cs_session.return_value.__enter__ = Mock(return_value=mock_cs_session_obj)
                    mock_log_obj = Mock()
                    mock_logger.return_value.__enter__ = Mock(return_value=mock_log_obj)

                    mock_resource_value = Mock()
                    self.os_shell_api.model_parser.deployed_app_resource_from_context_remote = Mock(
                        return_value=mock_resource_value)

                    mock_full_name = 'test_full_name'
                    mock_context_remote = Mock()
                    mock_context_remote.fullname = mock_full_name

                    self.command_context.remote_endpoints = [mock_context_remote]

                    self.os_shell_api.power_operation.power_on = Mock(return_value=True)
                    self.os_shell_api.power_on(self.command_context)

                    self.os_shell_api.power_operation.power_on.assert_called_with(
                        openstack_session=self.os_shell_api.os_session_provider.get_openstack_session(),
                        deployed_app_resource=mock_resource_value,
                        cloudshell_session=mock_cs_session_obj,
                        resource_fullname=mock_full_name,
                        logger=mock_log_obj)

    def test_power_off(self):
        with patch('cloudshell.cp.openstack.openstack_shell.LoggingSessionContext', autospec=True) as mock_logger:
            with patch('cloudshell.cp.openstack.openstack_shell.ErrorHandlingContext'):
                with patch('cloudshell.cp.openstack.openstack_shell.CloudShellSessionContext') as mock_cs_session:

                    mock_cs_session_obj = Mock()
                    mock_cs_session.return_value.__enter__ = Mock(return_value=mock_cs_session_obj)
                    mock_log_obj = Mock()
                    mock_logger.return_value.__enter__ = Mock(return_value=mock_log_obj)

                    mock_resource_value = Mock()
                    self.os_shell_api.model_parser.deployed_app_resource_from_context_remote = Mock(
                        return_value=mock_resource_value)

                    mock_full_name = 'test_full_name'
                    mock_context_remote = Mock()
                    mock_context_remote.fullname = mock_full_name

                    self.command_context.remote_endpoints = [mock_context_remote]

                    self.os_shell_api.power_operation.power_off = Mock(return_value=True)
                    self.os_shell_api.power_off(self.command_context)

                    self.os_shell_api.power_operation.power_off.assert_called_with(
                        openstack_session=self.os_shell_api.os_session_provider.get_openstack_session(),
                        deployed_app_resource=mock_resource_value,
                        cloudshell_session=mock_cs_session_obj,
                        resource_fullname=mock_full_name,
                        logger=mock_log_obj)

    def test_deploy_instance_returns_deploy_result(self):
        """
        Tests deploy_instance method with deploy_result assertions.
        :return:
        """
        mock_logger = Mock()

        dep_atts_json = '[{"attributeName":"Auto Delete","attributeValue":"True","type":"attributes"},{"attributeName":"Autoload","attributeValue":"True","type":"attributes"},{"attributeName":"IP Regex","attributeValue":"","type":"attributes"},{"attributeName":"Refresh IP Timeout","attributeValue":"600","type":"attributes"},{"attributeName":"vCenter VM","attributeValue":"Tor/Temps/ImageMonoNew","type":"attributes"},{"attributeName":"vCenter VM Snapshot","attributeValue":"1","type":"attributes"},{"attributeName":"VM Cluster","attributeValue":"","type":"attributes"},{"attributeName":"VM Storage","attributeValue":"","type":"attributes"},{"attributeName":"VM Resource Pool","attributeValue":"","type":"attributes"},{"attributeName":"VM Location","attributeValue":"","type":"attributes"},{"attributeName":"Auto Power On","attributeValue":"True","type":"attributes"},{"attributeName":"Auto Power Off","attributeValue":"True","type":"attributes"},{"attributeName":"Wait for IP","attributeValue":"True","type":"attributes"},{"attributeName":"Password","attributeValue":"3M3u7nkDzxWb0aJ/IZYeWw==","type":"attributes"},{"attributeName":"Public IP","attributeValue":"","type":"attributes"},{"attributeName":"User","attributeValue":"","type":"attributes"},{"attributeName":"Cloud Provider","attributeValue":"test_cloud_provider","type":"attributes"},{"attributeName":"Availability Zone","attributeValue":"test_availability_zone","type":"attributes"},{"attributeName":"Image ID","attributeValue":"test_image_uuid","type":"attributes"},{"attributeName":"Instance Flavor","attributeValue":"test_instance_flavor","type":"attributes"},{"attributeName":"Add Floating IP","attributeValue":"True","type":"attributes"},{"attributeName":"Autoload","attributeValue":"1","type":"attributes"},{"attributeName":"Floating IP Subnet ID","attributeValue":"floating_ip_subnet_id","type":"attributes"},{"attributeName":"Affinity Group ID","attributeValue":"affinity_group_id","type":"attributes"},{"attributeName":"Auto udev","attributeValue":"True","type":"attributes"}]'
        resource_atts_json = '[{"attributeName":"Password","attributeValue":"3M3u7nkDzxWb0aJ/IZYeWw==","type":"attributes"},{"attributeName":"Public IP","attributeValue":"","type":"attributes"},{"attributeName":"User","attributeValue":"","type":"attributes"}]'
        deploy_req_json = '{"driverRequest":{"actions":[{"actionParams":{"appName":"test_deploy_appname","deployment":{"deploymentPath":"OpenStack Deploy From Glance Image","attributes": ' + dep_atts_json +' ,"type":"deployAppDeploymentInfo"},"appResource":{"attributes":'+ resource_atts_json +',"type":"appResourceInfo"},"type":"deployAppParams"},"actionId":"7808cf76-b8c5-4392-b571-5da99836b84b","type":"deployApp"}]}}'

        with patch('cloudshell.cp.openstack.openstack_shell.LoggingSessionContext', autospec=True) as mock_logger:
            mock_log_obj = Mock()
            mock_logger.return_value.__enter__ = Mock(return_value=mock_log_obj)
            with patch('cloudshell.cp.openstack.openstack_shell.ErrorHandlingContext'):
                with patch('cloudshell.cp.openstack.openstack_shell.CloudShellSessionContext'):

                    parser = DriverRequestParser()
                    parser.add_deployment_model(DeployOSNovaImageInstanceDeploymentModel)


                    deployapp_req =  single(parser.convert_driver_request_to_actions(jsonpickle.decode(deploy_req_json)), lambda x: isinstance(x, DeployApp))

                    if isinstance(deployapp_req,DeployApp):
                        pass


                    deploy_result = DeployResultModel(vm_name=deployapp_req.actionParams.appName,
                                                      vm_uuid='1234-56',
                                                      deployed_app_ip="10.1.1.1",
                                                      deployed_app_attributes={'Public IP':'test_public_ip'},
                                                      floating_ip="4.3.2.1",
                                                      vm_details_data='')

                    self.os_shell_api.deploy_operation.deploy = Mock(return_value=deploy_result)

                    cancellation_context = Mock()
                    os_cloud_provider = OpenStackResourceModel()
                    res = self.os_shell_api.deploy_instance_from_image(command_context=self.command_context,
                                                                       deploy_app_action=deployapp_req,
                                                                       cancellation_context=cancellation_context)

                    decoded_res = jsonpickle.decode(res)
                    self.assertEqual(decoded_res['vm_name'], deployapp_req.actionParams.appName)
                    self.assertEqual(decoded_res['vm_uuid'], deploy_result.vm_uuid)
                    self.assertEqual(decoded_res['deployed_app_address'], deploy_result.deployed_app_address)
                    self.assertEqual(decoded_res['deployed_app_attributes'], deploy_result.deployed_app_attributes)
                    self.assertEqual(decoded_res['floating_ip'], deploy_result.floating_ip)

    def test_delete_instance(self):
        """

        :return:
        """
        # mock_logger = Mock()
        with patch('cloudshell.cp.openstack.openstack_shell.LoggingSessionContext', autospec=True) as mock_logger:
            with patch('cloudshell.cp.openstack.openstack_shell.ErrorHandlingContext'):
                with patch('cloudshell.cp.openstack.openstack_shell.CloudShellSessionContext'):
                    mock_log_obj = Mock()
                    mock_logger.return_value.__enter__ = Mock(return_value=mock_log_obj)
                    mock_resource_value = Mock()
                    self.os_shell_api.model_parser.deployed_app_resource_from_context_remote = Mock(return_value=mock_resource_value)
                    mock_context_remote = Mock()
                    mock_context_remote.full_name = 'test full name'

                    test_floating_ip = '1.2.3.4'
                    mock_context_remote.attributes = {'Public IP': test_floating_ip}

                    self.command_context.remote_endpoints = [mock_context_remote]

                    self.os_shell_api.hidden_operation.delete_instance = Mock(return_value=True)
                    self.os_shell_api.delete_instance(self.command_context)

                    self.os_shell_api.hidden_operation.delete_instance.assert_called_with(
                        openstack_session=self.os_shell_api.os_session_provider.get_openstack_session(),
                        deployed_app_resource=mock_resource_value,
                        floating_ip=test_floating_ip,
                        logger=mock_log_obj)

    def test_refresh_ip(self):
        """

        :return:
        """
        with patch('cloudshell.cp.openstack.openstack_shell.LoggingSessionContext', autospec=True) as mock_logger:
            with patch('cloudshell.cp.openstack.openstack_shell.ErrorHandlingContext'):
                with patch('cloudshell.cp.openstack.openstack_shell.CloudShellSessionContext') as mock_cs_session:

                    mock_cs_session_obj = Mock()
                    mock_cs_session.return_value.__enter__ = Mock(return_value=mock_cs_session_obj)
                    mock_log_obj = Mock()
                    mock_logger.return_value.__enter__ = Mock(return_value=mock_log_obj)

                    mock_resource_value = Mock()
                    self.os_shell_api.model_parser.deployed_app_resource_from_context_remote = Mock(
                        return_value=mock_resource_value)

                    mock_private_ip = '1.2.3.4'
                    mock_public_ip = '4.3.2.1'
                    mock_full_name = 'test full name'
                    mock_context_remote = Mock()
                    mock_context_remote.fullname = mock_full_name
                    mock_context_remote.address = mock_private_ip
                    mock_context_remote.attributes = {'Public IP': mock_public_ip}

                    self.command_context.remote_endpoints = [mock_context_remote]

                    mock_cp_resource_model = Mock()
                    self.os_shell_api.model_parser.get_resource_model_from_context = Mock(
                        return_value=mock_cp_resource_model)

                    self.os_shell_api.refresh_ip_operation.refresh_ip = Mock(return_value=True)
                    self.os_shell_api.refresh_ip(self.command_context)


                    self.os_shell_api.refresh_ip_operation.refresh_ip.assert_called_with(
                        openstack_session=self.os_shell_api.os_session_provider.get_openstack_session(),
                        deployed_app_resource=mock_resource_value,
                        private_ip=mock_private_ip,
                        resource_fullname=mock_full_name,
                        cloudshell_session=mock_cs_session_obj,
                        cp_resource_model=mock_cp_resource_model,
                        logger=mock_log_obj)

    def test_get_inventory(self):
        """

        :return:
        """
        with patch('cloudshell.cp.openstack.openstack_shell.LoggingSessionContext', autospec=True) as mock_logger:
            with patch('cloudshell.cp.openstack.openstack_shell.ErrorHandlingContext'):
                with patch('cloudshell.cp.openstack.openstack_shell.CloudShellSessionContext') as mock_cs_session:
                    mock_cs_session_obj = Mock()
                    mock_cs_session.return_value.__enter__ = Mock(return_value=mock_cs_session_obj)
                    mock_log_obj = Mock()
                    mock_logger.return_value.__enter__ = Mock(return_value=mock_log_obj)

                    mock_cp_resource_model = Mock()
                    self.os_shell_api.model_parser.get_resource_model_from_context = Mock(
                        return_value=mock_cp_resource_model)

                    self.os_shell_api.autoload_operation.get_inventory = Mock()
                    self.os_shell_api.get_inventory(self.command_context)

                    self.os_shell_api.autoload_operation.get_inventory.assert_called_with(
                        openstack_session=self.os_shell_api.os_session_provider.get_openstack_session(),
                        cs_session=mock_cs_session_obj,
                        cp_resource_model=mock_cp_resource_model,
                        logger=mock_log_obj)
