
class CommandCancellationException(Exception):
    """
    This exception is raised when command is cancelled.
    """
    pass


class CommandCancellationService(object ):

    def check_if_cancelled(self, cancellation_context):
        """
        Check if command was cancelled from cloudshell

        :param cancellation_context:
        :return:
        """

        if cancellation_context.is_cancelled:
            raise CommandCancellationException("Command was Cancelled")

        return None
