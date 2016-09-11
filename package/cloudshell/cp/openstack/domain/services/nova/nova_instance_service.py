"""
Implements InstanceService class, that allows one to
\'start/stop/delete/terminate\' OpenStack instances.
"""
from novaclient import client as novaclient
from cloudshell.cp.openstack.common.driver_helper import CloudshellDriverHelper

class NovaInstanceService(object):
    """Implements management of Compute Instances."""
    API_VERSION = '2.0'

    def __init__(self, instance_waiter):
        self.instance_waiter = instance_waiter
        # We do not 'create client object right now' we create client object
        # in create_instance. This automatically means none of the methods
        # can be called without a proper client object

    def create_instance(self, openstack_session, name, reservation,
                        cp_resource_model, deploy_req_model, logger):
        """
        :param keystoneauth1.session.Session openstack_session: Keystone Session
        :param str name: Name of Instance
        :param ReservationModel reservation: Reservation Model
        :param OpenStackResourceModel cp_resource_model:
        :param DeployOSNovaImageInstanceResourceModel deploy_req_model: Details of the Image to be deployed
        :param LoggingSessionContext logger:
        :rtype novaclient.Client.servers.Server:
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

        # Quali Network - Quali Network UUID is a OpenStack Resource Model attribute
        qnet_dict = {'net-id': cp_resource_model.qs_mgmt_os_net_uuid}

        uniq = CloudshellDriverHelper.get_uuid() #str(uuid.uuid4()).split("-")[0]
        name = name + "-" + uniq
        instance = client.servers.create(name=name,
                                         image=img_obj,
                                         flavor=flavor_obj,
                                         nics=[qnet_dict])

        # instance_attrrs = instance.get
        # FIXME : Wait for the server to be ready
        self.instance_waiter.wait(instance, state=self.instance_waiter.ACTIVE)
        return instance

    def terminate_instance(self, openstack_session, instance_id, logger):
        """
        :param keystoneauth1.session.Session openstack_session:
        :param str instance_id: Instance ID to be terminated
        :param LoggingSessionContext logger:
        :rtype Boolean:
        """
        logger.info("Deleting instance with instance ID {0}".format(instance_id))

        if not openstack_session or not instance_id or not logger:
            raise ValueError("Any of openstack_session, instance_id can be None")

        client = novaclient.Client(self.API_VERSION, session=openstack_session)
        instance = self.get_instance_from_instance_id(openstack_session=openstack_session,
                                                      instance_id=instance_id,
                                                      logger=logger,
                                                      client=client)
        if instance is None:
            logger.info("Instance with Instance ID {0} does not exist. Already Deleted?".format(instance_id))
        else:
            client.servers.delete(instance)

    def instance_power_on(self, openstack_session, instance_id, logger):
        """
        call instance.start() for the instance for a given instance_id

        :param keystoneauth1.session.Session openstack_session:
        :param str instance_id:
        :param LoggingSessionContext logger:
        :rtype None:
        """
        client = novaclient.Client(self.API_VERSION, session=openstack_session)
        instance = self.get_instance_from_instance_id(openstack_session=openstack_session,
                                                      instance_id=instance_id,
                                                      logger=logger,
                                                      client=client)

        if instance is None:
            logger.info("Instance with Instance ID {0} does not exist. Already Deleted?".format(instance_id))
        else:

            if instance.status != self.instance_waiter.ACTIVE:
                instance.start()
                self.instance_waiter.wait(instance, self.instance_waiter.ACTIVE)

    def instance_power_off(self, openstack_session, instance_id, logger):
        """
        call instance.stop() for the instance for a given instance_id

        :param keystoneauth1.session.Session openstack_session:
        :param str instance_id:
        :param LoggingSessionContext logger:
        :rtype None:
        """
        client = novaclient.Client(self.API_VERSION, session=openstack_session)
        instance = self.get_instance_from_instance_id(openstack_session=openstack_session,
                                                      instance_id=instance_id,
                                                      logger=logger,
                                                      client=client)

        if instance is None:
            logger.info("Instance with Instance ID {0} does not exist. Already Deleted?".format(instance_id))
        else:

            if instance.status != self.instance_waiter.SHUTOFF:
                instance.stop()
                self.instance_waiter.wait(instance, self.instance_waiter.SHUTOFF)

    def get_security_groups(self, openstack_session, instance):
        """
        :param keystoneauth1.session.Session openstack_session:
        :param novaclient.Client.servers.Server instance:
        :rtype dict: Dictionary of Security Groups attached to instance.
        """
        pass

    def get_interfaces(self, instance):
        """
        :param novaclient.Client.servers.Server instance:
        :rtype dict: Dictionary of Interfaces attached (gives IP addrsses)
        """
        pass

    def assign_floating_ip(self, instance):
        """
        :param novaclient.Client.servers.Server instance:
        :rtype dict: Dictionary of Security Groups attached to instance.
        """
        pass

    def get_private_ip(self, instance):
        """

        :param novaclient.Client.servers.Server instance:
        :rtype str: Instance IP
        """
        if not instance:
            return ""

        ip = ""
        for net_name, net_ips in instance.networks.iteritems():
            if net_name == 'quali-network':
                ip = net_ips[0] if net_ips else ""
                break

        return ip

    def get_instance_from_instance_id(self, openstack_session, instance_id, logger, client=None):
        """
        Returns an instance, given instance_id for the openstack_session. Optionally takes novaclient Object

        :param keystoneauth1.session.Sesssion openstack_session:
        :param str instance_id:
        :param LoggingSessionContext logger:
        :param novaclient.Client client: client (optional)
        :rtype novaclient.Client.servers.Server instance:
        """
        if client is None:
            client = novaclient.Client(self.API_VERSION, session=openstack_session)
        try:
            instance = client.servers.find(id=instance_id)
            return instance
        except novaclient.exceptions.NotFound:
            logger.info("Instance with instance ID {0} Not Found".format(instance_id))
            return None
        except Exception:
            raise
