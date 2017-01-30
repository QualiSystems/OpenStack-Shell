from unittest import TestCase
from mock import Mock

from cloudshell.cp.openstack.command.operations.connectivity_operation import ConnectivityOperation

class TestConnectivityOperation(TestCase):
    def setUp(self):
        self.connectivity_service = Mock()
        self.conn_operation = ConnectivityOperation(connectivity_service=self.connectivity_service)
        self.conn_operation.connectivity_service = Mock()
        self.os_session = Mock()
        self.cp_resource_model = Mock()
        self.logger = Mock()
        pass

    def test_connectivity_operation_apply_connectivity(self):
        connectivity_request = Mock()
        mock_result = Mock()
        #self.conn_operation.apply_connectivity = Mock(return_value=mock_result)

        self.conn_operation.apply_connectivity(openstack_session=self.os_session,
                                               cp_resource_model=self.cp_resource_model,
                                               conn_request=connectivity_request,
                                               logger=self.logger)

        self.conn_operation.connectivity_service.perform_apply_connectivity.assert_called_with(
                                                                    openstack_session=self.os_session,
                                                                    cp_resource_model=self.cp_resource_model,
                                                                    connection_request=connectivity_request,
                                                                    logger=self.logger)

