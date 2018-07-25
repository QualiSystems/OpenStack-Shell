import traceback
from cloudshell.cp.core.models import  VmDetailsData


class VmDetailsOperation(object):
    def __init__(self, vm_details_provider, instance_service):
        """
        :type vm_details_provider: cloudshell.cp.openstack.domain.common.vm_details_provider.VmDetailsProvider
        """
        self.vm_details_provider = vm_details_provider
        self.instance_service = instance_service

    def get_vm_details(self, openstack_session, requests, cancellation_context, logger, management_vlan_id):
        """
        :param management_vlan_id:
        :param requests:
        :param keystoneauth1.session.Session openstack_session:
        :param cancellation_context:
        :param logging.Logger logger:
        """

        results = []
        for request in requests:
            if cancellation_context.is_cancelled:
                break

            vm_name = request.deployedAppJson.name
            instance_id = request.deployedAppJson.vmdetails.uid

            try:
                vm = self.instance_service.get_instance_from_instance_id(openstack_session=openstack_session,
                                                                         instance_id=instance_id,
                                                                         logger=logger)
                result = self.vm_details_provider.create(vm, openstack_session, management_vlan_id, logger)
            except Exception as e:
                logger.error("Error getting vm details for '{0}': {1}".format(vm_name, traceback.format_exc()))
                result = VmDetailsData(errorMessage=e.message)

            result.appName = vm_name
            results.append(result)

        return results
