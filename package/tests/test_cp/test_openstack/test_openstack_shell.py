from unittest import TestCase
import jsonpickle
from mock import Mock, patch

from cloudshell.cp.openstack.openstack_shell import OpenStackShell
from cloudshell.cp.openstack.models.openstack_resource_model import OpenStackResourceModel
from cloudshell.cp.openstack.models.deploy_os_nova_image_instance_resource_model import DeployOSNovaImageInstanceResourceModel
from cloudshell.cp.openstack.models.deploy_result_model import DeployResultModel

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

    def test_power_on(self):
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
        with patch('cloudshell.cp.openstack.openstack_shell.LoggingSessionContext', autospec=True) as mock_logger:
            mock_log_obj = Mock()
            mock_logger.return_value.__enter__ = Mock(return_value=mock_log_obj)
            with patch('cloudshell.cp.openstack.openstack_shell.ErrorHandlingContext'):
                with patch('cloudshell.cp.openstack.openstack_shell.CloudShellSessionContext'):
                    app_name = 'test_deploy_appname'
                    deploy_res_mock = DeployOSNovaImageInstanceResourceModel()
                    deploy_res_mock.auto_power_off = "True"
                    deploy_res_mock.auto_delete = "True"
                    deploy_res_mock.autoload = "True"
                    deploy_res_mock.cloud_provider = "test_cloud_provider"

                    self.os_shell_api.model_parser.deploy_res_model_appname_from_deploy_req = Mock(return_value=(deploy_res_mock,
                                                                                                    app_name))

                    deploy_result = DeployResultModel(vm_name=app_name,
                                                      vm_uuid='1234-56',
                                                      cloud_provider_name=deploy_res_mock.cloud_provider,
                                                      deployed_app_ip="10.1.1.1")

                    self.os_shell_api.deploy_operation.deploy = Mock(return_value=deploy_result)

                    os_cloud_provider = OpenStackResourceModel()
                    res = self.os_shell_api.deploy_instance_from_image(self.command_context, os_cloud_provider)

                    decoded_res = jsonpickle.decode(res)
                    self.assertEqual(decoded_res['vm_name'], app_name)
                    self.assertEqual(decoded_res['vm_uuid'], deploy_result.vm_uuid)
                    self.assertEqual(decoded_res['cloud_provider_resource_name'], deploy_res_mock.cloud_provider)
                    self.assertEqual(decoded_res['deployed_app_address'], deploy_result.deployed_app_address)

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

                    self.command_context.remote_endpoints = [mock_context_remote]

                    self.os_shell_api.hidden_operation.delete_instance = Mock(return_value=True)
                    self.os_shell_api.delete_instance(self.command_context)

                    self.os_shell_api.hidden_operation.delete_instance.assert_called_with(
                        openstack_session=self.os_shell_api.os_session_provider.get_openstack_session(),
                        deployed_app_resource=mock_resource_value,
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
                    mock_full_name = 'test full name'
                    mock_context_remote = Mock()
                    mock_context_remote.fullname = mock_full_name
                    mock_context_remote.address = mock_private_ip

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

