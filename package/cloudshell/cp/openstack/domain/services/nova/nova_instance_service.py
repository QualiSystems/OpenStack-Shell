"""
Implements InstanceService class, that allows one to
\'start/stop/delete/terminate\' OpenStack instances.
"""
from novaclient import client as novaclient
from cloudshell.cp.openstack.common.driver_helper import CloudshellDriverHelper

import traceback
import jsonpickle


class NovaInstanceService(object):
    """Implements management of Compute Instances."""
    API_VERSION = '2.0'

    def __init__(self, instance_waiter):
        self.instance_waiter = instance_waiter
        # We do not 'create client object right now' we create client object
        # in create_instance. This automatically means none of the methods
        # can be called without a proper client object

    def create_instance(self, openstack_session, name, reservation,
                        cp_resource_model, deploy_req_model, cancellation_context, logger):
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

        logger.info("Creating OpenStack Instance for Image: {0}, Flavor: {1}".format(deploy_req_model.img_uuid,
                                                                                     deploy_req_model.instance_flavor))
        # FIXME: Add other arguments as kwargs
        img_obj = client.images.find(id=deploy_req_model.img_uuid)
        flavor_obj = client.flavors.find(name=deploy_req_model.instance_flavor)

        # Quali Network - Quali Network UUID is a OpenStack Resource Model attribute
        qnet_dict = {'net-id': cp_resource_model.qs_mgmt_os_net_uuid}

        uniq = CloudshellDriverHelper.get_uuid() #str(uuid.uuid4()).split("-")[0]
        name = name + "-" + uniq
        instance = client.servers.create(name=name,
                                         image=img_obj,
                                         flavor=flavor_obj,
                                         nics=[qnet_dict])
        try:
            logger.error("cancellation_context.is_cancelled: {}".format(cancellation_context.is_cancelled))
            self.instance_waiter.wait(instance, state=self.instance_waiter.ACTIVE,
                                      cancellation_context=cancellation_context, logger=logger)
        except Exception as e:
            if instance:
                client.servers.delete(instance)
            raise

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
            raise ValueError("Instance with Instance ID {0} does not exist. May be deleted already?".format(instance_id))
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
            raise ValueError("Instance with Instance ID {0} not found. May be deleted already?".format(instance_id))
        else:
            if instance.status != self.instance_waiter.SHUTOFF:
                instance.stop()
                self.instance_waiter.wait(instance, self.instance_waiter.SHUTOFF)

    def get_instance_mgmt_network_name(self, instance, openstack_session, cp_resource_model):
        """

        :param novaclient.Client.servers.Server instance:
        :param keystoneauth1.session.Sesssion openstack_session:
        :param OpenStackResourceModel cp_resource_model:
        :rtype str: Network Name
        """

        client = novaclient.Client(self.API_VERSION, session=openstack_session)

        for net in client.networks.list():
            net_dict = net.to_dict()
            if net_dict['id'] == cp_resource_model.qs_mgmt_os_net_uuid:
                return net_dict['label']

        return None

    def get_private_ip(self, instance, private_network_name):
        """

        :param novaclient.Client.servers.Server instance:
        :param str private_network_name:
        :rtype str: Instance IP
        """
        if not instance:
            return ""

        ip = ""

        for net_name, net_ips in instance.networks.iteritems():
            if net_name == private_network_name:
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

    # FIXME: Both the methods should return some kind of an object
    # result: Success/Failure
    # Error Message: To be displayed.
    def attach_nic_to_net(self, openstack_session, instance_id, net_id, logger):
        """

        :param openstack_session:
        :param instance_id:
        :param net_id:
        :param logger:
        :return:
        """

        instance = self.get_instance_from_instance_id(openstack_session=openstack_session,
                                                      instance_id=instance_id,
                                                      logger=logger)
        if instance is None :
            return None

        try:
            res = instance.interface_attach(net_id=net_id, port_id=None, fixed_ip=None)
            iface_mac = res.to_dict().get('mac_addr')
            iface_portid = res.to_dict().get('port_id')
            iface_ip = res.to_dict().get('fixed_ips')[0]['ip_address']
            result = jsonpickle.dumps({'ip_address':iface_ip, 'port_id':iface_portid, 'mac_address':iface_mac})
            # result = "/".join([iface_ip, iface_portid, iface_mac])
            return result
        except Exception as e:
            logger.error("Exception: {0} during interface attach.".format(e))
            raise

        return None

    def detach_nic_from_instance(self, openstack_session, instance_id, port_id, logger):
        """

        :param keystoneauth1.session.Session openstack_session:
        :param str instance_id:
        :param str port_id:
        :param LoggingSesssionContext logger:
        :return bool: Success or Failure
        """

        logger.info("Detaching port {0} from Instance {1}".format(port_id, instance_id))
        instance = self.get_instance_from_instance_id(openstack_session=openstack_session,
                                                      instance_id=instance_id,
                                                      logger=logger)
        logger.info("Returned instance {0}".format(instance))
        if instance is None:
            return False

        try:
            instance.interface_detach(port_id)

            return True

        except Exception as e:
            logger.error(traceback.format_exc())
            return False

    def assign_floating_ip(self, instance, openstack_session, cp_resource_model, floating_ip_net_uuid, logger):
        """

        :param novaclient.Client.servers.Server instance:,
        :param keystoneauth1.session.Session openstack_session:
        :param OpenStackResourceModel cp_resource_model:
        :param str floating_ip_net_uuid:
        :param LoggingSessionContext logger:
        :return str: Floating IP as a string.
        """

        client = novaclient.Client(self.API_VERSION, session=openstack_session)

        floating_ip_net_name = ''
        for net in client.networks.list():
            net_dict = net.to_dict()
            if net_dict['id'] == floating_ip_net_uuid:
                floating_ip_net_name = net_dict['label']

        if not floating_ip_net_name:
            raise ValueError("Cannot find a network with ID {0}".format(floating_ip_net_name))

        floating_ip_obj = client.floating_ips.create(floating_ip_net_name)
        instance.add_floating_ip(floating_ip_obj)

        return floating_ip_obj.ip

    def delete_floating_ip(self, openstack_session, floating_ip):
        """

        :param keystoneauth1.session.Session openstack_session:
        :param str floating_ip:
        :return: None
        """

        client = novaclient.Client(self.API_VERSION, session=openstack_session)

        # We need to get the ID
        floating_ip_objid = ''
        for fl in client.floating_ips.list():
            if fl.ip == floating_ip:
                floating_ip_objid = fl.id
                break

        if floating_ip_objid:
            client.floating_ips.delete(floating_ip_objid)
