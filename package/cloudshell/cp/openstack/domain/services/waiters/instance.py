"""Synchronous Instance waiter"""

import time

class InstanceWaiterTimeoutException(Exception):
    pass

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
        :param delay: Time in seconds between each poll
        :type delay: int
        :param timeout: Timeout after which Exception will be raised
        :type timeout: int
        """
        self.cancellation_service = cancellation_service
        self.delay = delay

    def wait(self, instance, state, cancellation_context, logger):
        """
        Waits till cancelled.

        :param instance: Instance to be waited on
        :type instance: novaclient.v2.servers.Server
        :param state:
        :type state: str
        :param cancellation_context:
        :type cancellation_context:
        :return: novaclient.v2.servers.Server (updated)
        """

        if state not in self.INSTANCE_STATES:
            raise ValueError('Unsupported Instance State {0}'.format(state))

        while instance.status != state:
            instance.get()
            self.cancellation_service.check_if_cancelled(cancellation_context=cancellation_context)
            time.sleep(self.delay)
            logger.error("after instance.status: {} , state: {}".format(instance.status, state))

        return instance
