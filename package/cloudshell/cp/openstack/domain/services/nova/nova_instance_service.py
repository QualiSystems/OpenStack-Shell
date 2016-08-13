"""
Implements InstanceService class, that allows one to
\'start/stop/delete/terminate\' OpenStack instances.
"""

from novaclient import client as novaclient

class NovaInstanceService(object):
    """Implements management of Compute Instances."""
    API_VERSION = '2.0'

    def __init__(self, instance_waiter):
        self.instance_waiter = instance_waiter
        # We do not 'create client object right now' we create client object
        # in create_instance. This automatically means none of the methods
        # can be called without a proper client object

    def create_instance(self, openstack_session, name, reservation,
                        deploy_req_model, logger):
        """
        :param openstack_session: Keystone Session
        :type openstack_session: keystoneauth1.session.Session
        :param name: Name of Instance
        :type name: str
        :param reservation: Reservation Model
        :type reservation: FIXME
        :param deploy_req_model: Details of the Image to be deployed
        :type deploy_req_model: cloudshell.cp.openstack.models.deploy_os_nova_image_instance_model.DeployOSNovaImageInstanceResourceModel
        :param logger:
        :type logger:
        :return novaclient.Client.servers.Server:
        """

        if not openstack_session or not name or not reservation or \
                not deploy_req_model:
            return None

        client = novaclient.Client(self.API_VERSION, session=openstack_session)

        logger.info("Creating OpenStack Instance for Image: {0}, Flavor: {1}".format(deploy_req_model.img_name,
                                                                                     deploy_req_model.instance_flavor))
        # FIXME: Add other arguments as kwargs
        img_obj = client.images.find(name=deploy_req_model.img_name)
        flavor_obj = client.flavors.find(name=deploy_req_model.instance_flavor)
        # Quali Network - FIXME: Remove hard coded (get it from network service)
        qnet_obj = client.networks.find(label='quali-network')
        qnet_dict = {'net-id':qnet_obj.id}
        instance = client.servers.create(name=name,
                                         image=img_obj,
                                         flavor=flavor_obj,
                                         nics=[qnet_dict])

        if not instance:
            return None

        # instance_attrrs = instance.get
        # FIXME : Wait for the server to be ready
        self.instance_waiter.wait(instance, state=self.instance_waiter.ACTIVE)
        return instance

    def terminate_instance(self, openstack_session, instance):
        """
        :param openstack_session:
        :type openstack_session:
        :param instance: Instance to be terminated
        :type instance: novalcient.Client.servers.Server
        :return novaclient.Client.servers.Server:
        """
        client = novaclient.Client(self.API_VERSION, session=openstack_session)
        client.servers.delete(instance)
        return self.instance_waiter.wait(instance,
                                        state=self.instance_waiter.DELETED)


    def get_security_groups(self, openstack_session, instance):
        """
        :param openstack_session:
        :type openstack_session:
        :param instance:
        :type instance: novaclient.Client.servers.Server
        :return dict: Dictionary of Security Groups attached to instance.
        """
        pass

    def get_interfaces(self, instance):
        """
        :param instance:
        :type instance: novaclient.Client.servers.Server
        :return dict: Dictionary of Interfaces attached (gives IP addrsses)
        """
        pass

    def assign_floating_ip(self, instance):
        """
        :param instance:
        :type instance: novaclient.Client.servers.Server
        :return dict: Dictionary of Security Groups attached to instance.
        """
        pass
