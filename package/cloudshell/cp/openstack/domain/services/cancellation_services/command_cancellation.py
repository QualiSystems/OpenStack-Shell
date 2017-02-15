from cloudshell.cp.openstack.models.exceptions import CommandCancellationException


class CommandCancellationService(object):

    def check_if_cancelled(self, cancellation_context):
        """
        Check if command was cancelled from cloudshell

        :param cloudshell.shell.core.context.CancellationContext cancellation_context:
        :return:
        """

        if cancellation_context.is_cancelled:
            raise CommandCancellationException("Command was Cancelled")

        return None
