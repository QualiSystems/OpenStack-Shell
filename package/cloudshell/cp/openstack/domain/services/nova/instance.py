"""
Implements InstanceService class, that allows one to
\'start/stop/delete/terminate\' OpenStack instances.
"""

from novaclient import client as novaclient

class InstanceService(object):
    """Implements management of Compute Instances."""
    API_VERSION = '2.0'

    def __init__(self, instance_waiter):
        self.instance_waiter = instance_waiter

    def create_instance(self, openstack_session, name, reservation,
                        deployment_info):
        """
        :param openstack_session: Keystone Session
        :type openstack_session: keystoneauth1.session.Session
        :param name: Name of Instance
        :type name: str
        :param reservation: Reservation Model
        :type reservation: FIXME
        :param deployment_info: Details of the Image to be deployed
        :type deployment_info: FIXME
        :return novaclient.Client.servers.Server:
        """

        if not openstack_session or not name or not reservation or \
                not deployment_info:
            return None

        client = novaclient.Client(API_VERSION, session=openstack_session)

        # FIXME: Add other arguments as kwargs
        instance = client.servers.create(name, deployment_info.image_name,
                                    deployment_info.flavor_name)

        # FIXME : Wait for the server to be ready
        self.instance_waiter.wait(instance, state=self.instance_waiter.ACTIVE)

        return instance

    def terminate_instance(self, instance):
        """
        :param instance: Instance to be terminated
        :type instance: novalcient.Client.servers.Server
        :return novaclient.Client.servers.Server:
        """
        client = novaclient.Client(API_VERSION, session=openstack_session)
        client.servers.delete(instance)
        return self.instance_waiter.wait(instance,
                                        state=self.instance_waiter.DELETED)
