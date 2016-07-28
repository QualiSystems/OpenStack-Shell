"""Synchronous Instance waiter"""

import time

class InstanceWaiterTimeoutException(Exception):
    pass

class InstanceWaiter(object):
    """An instance waiter class that implements a synchronous waiter that
    waits till the instance reaches a state.
    """
    # FIXME : support other states.
    ACTIVE = u'ACTIVE'
    ERROR = u'ERROR'
    BUILDING = u'BUILDING'
    STOPPED = u'STOPPED'
    DELETED = u'DELETED'

    INSTANCE_STATES = [ BUILDING, ACTIVE, STOPPED, DELETED, ERROR]
    def __init__(self, delay=2, timeout=10):
        """
        :param delay: Time in seconds between each poll
        :type delay: int
        :param timeout: Timeout after which Exception will be raised
        :type timeout: int
        """
        self.delay = delay
        self.timeout = timeout * SECS


    def wait(self, instance, state):
        """
        :param instance: Instance to be waited on
        :type instance: novaclient.v2.servers.Server
        :param state:
        :type state: str
        :return: novaclient.v2.servers.Server (updated)
        """
        start_time = time.time()

        if state not in self.INSTANCE_STATES:
            raise ValueError('Unsupported Instance State {0}'.format(state))

        while time.time() - start_time >= self.timeout:
            instance.get()
                if instance.status == state:
                    return instance
                time.sleep(self.delay)
        raise InstanceWaiterTimeoutException('Maximum time exceeded waiting \
                                        for Instance {0}'.format(instance.name))
