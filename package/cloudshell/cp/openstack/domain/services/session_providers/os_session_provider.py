"""Implements a wrapper class for OpenStack session. Called by Shell Driver"""
from keystoneauth1 import identity as keystone_identity
from keystoneauth1 import session as keystone_session


class OpenStackSessionProvider(object):
    """A class that provides an OpenStack Session Object using the Password
    Authentication scheme of Keystone Identity service. Authentication is
    for 'default' domain of the user.
    """

    def __init__(self):
        """
        Simply allocates the object
        """
        pass

    def get_openstack_session(self, cloudshell_session, openstack_resource_model, logger):
        """
        :param cloudshell_session:
        :type cloudshell_session:
        :param openstack_resource_model:
        :type openstack_resource_model:
        :param logger:
        :type logger:
        :return keystoneauth1.session.Session:
        """
        return self._do_get_os_session(cloudshell_session,
                                        openstack_resource_model, logger)

    def _do_get_os_session(self, cs_session, os_res_model, logger):
        """

        :param cs_session:
        :param os_res_model:
        :param logger:
        :return:
        """
        if not cs_session or not os_res_model:
            return None

        logger.debug("Getting OpenStack Session:")
        logger.debug(os_res_model)
        username = os_res_model.os_user_name
        password = cs_session.DecryptPassword(os_res_model.os_user_password).Value
        project_name = os_res_model.os_project_name
        auth_url = os_res_model.controller_url
        proj_domain_id = os_res_model.os_domain_name
        user_domain_id = os_res_model.os_domain_name

        # FIXME: Can we use domain name below? Easier
        auth = keystone_identity.v3.Password(auth_url=auth_url,
                                            username=username,
                                            password=password,
                                            project_name=project_name,
                                            user_domain_id=user_domain_id,
                                            project_domain_id=proj_domain_id)

        return keystone_session.Session(auth=auth)
