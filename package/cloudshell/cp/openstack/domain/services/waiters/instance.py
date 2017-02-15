"""Synchronous Instance waiter"""

import time

from cloudshell.cp.openstack.models.exceptions import InstanceErrorStateException


class InstanceWaiter(object):
    """An instance waiter class that implements a synchronous waiter that
    waits till the instance reaches a state.
    """
    SECS = 60
    # FIXME : support other states.
    ACTIVE = u'ACTIVE'
    ERROR = u'ERROR'
    BUILDING = u'BUILDING'
    STOPPED = u'STOPPED'
    DELETED = u'DELETED'
    SHUTOFF = u'SHUTOFF'

    INSTANCE_STATES = [ACTIVE, ERROR, BUILDING, STOPPED, DELETED, SHUTOFF]

    def __init__(self, cancellation_service, delay=10):
        """
        :param int delay: Time in seconds between each poll
        """
        self.cancellation_service = cancellation_service
        self._delay = delay

    def wait(self, instance, state, cancellation_context, logger):
        """
        Waits till cancelled.

        :param novaclient.v2.servers.Server instance: Instance to be waited on
        :param str state:
        :param cloudshell.shell.core.context.CancellationContext cancellation_context:
        :return: novaclient.v2.servers.Server (updated)
        """

        if state not in self.INSTANCE_STATES:
            raise ValueError('Unsupported Instance State {0}'.format(state))

        while instance.status not in [state, self.ERROR]:
            instance.get()
            if cancellation_context is not None:
                self.cancellation_service.check_if_cancelled(cancellation_context=cancellation_context)
            time.sleep(self._delay)

        if instance.status == self.ERROR:
            raise InstanceErrorStateException(format(instance.fault['message']))

        return instance
