from unittest import TestCase
from mock import Mock

from cloudshell.cp.openstack.domain.services.session_providers.os_session_provider import OpenStackSessionProvider
from keystoneauth1 import identity as keystone_identity
from keystoneauth1 import session as keystone_session


class TestOpenStackSessionProvider(TestCase):
    def setUp(self):
        self.os_session_provider = OpenStackSessionProvider()

        self.os_res_model = Mock()
        self.os_res_model.os_user_name = 'testuser'
        self.os_res_model.controller_url = 'http://abc.com/'
        self.os_res_model.os_project_name = 'test_project'
        self.os_res_model.os_domain_name = 'test_domain'

        self.mock_logger = Mock()

    def test_get_openstack_session(self):

        cs_session = Mock()
        test_pass_str = 'test_password'
        test_pass = Mock()
        test_pass.Value = test_pass_str
        cs_session.DecryptPassword = Mock(return_value=test_pass)

        mock_auth = Mock()
        keystone_identity.v3.Password = Mock(return_value=mock_auth)

        mock_session = Mock()
        keystone_session.Session = Mock(return_value=mock_session)

        result = self.os_session_provider.get_openstack_session(cloudshell_session=cs_session,
                                                       openstack_resource_model=self.os_res_model,
                                                       logger=self.mock_logger)

        keystone_identity.v3.Password.assert_called_with(auth_url=self.os_res_model.controller_url,
                                                         username=self.os_res_model.os_user_name,
                                                         password=test_pass_str,
                                                         project_name=self.os_res_model.os_project_name,
                                                         user_domain_id=self.os_res_model.os_domain_name,
                                                         project_domain_id=self.os_res_model.os_domain_name)

        keystone_session.Session.assert_called_with(auth=mock_auth, verify=False)
        self.assertTrue(result, mock_session)
