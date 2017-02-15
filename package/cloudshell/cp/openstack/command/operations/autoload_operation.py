
class AutoLoadOperation(object):

    def __init__(self, cp_validator_service):
        """

        :param cp_validator_service:
        """
        self.cp_validator_service = cp_validator_service

    def get_inventory(self, openstack_session, cs_session, cp_resource_model, logger):
        """
        :param openstack_session:
        :param cs_session:
        :param cp_resource_model:
        :param logger:
        :return:
        """

        return self.cp_validator_service.validate_all(openstack_session=openstack_session,
                                                      cs_session=cs_session,
                                                      cp_resource_model=cp_resource_model,
                                                      logger=logger)