
from cloudshell.cp.openstack.domain.services.cp_validators.cp_validator import OpenStackCPValidator

class AutoLoadOperation(object):

    def __init__(self):
        self.cp_validator = OpenStackCPValidator()

    def get_inventory(self, openstack_session, cs_session, cp_resource_model, logger):
        """
        :param openstack_session:
        :param cs_session:
        :param cp_resource_model:
        :param logger:
        :return:
        """

        return self.cp_validator.validate_all(openstack_session=openstack_session,
                                               cs_session=cs_session,
                                               cp_resource_model=cp_resource_model,
                                               logger=logger)