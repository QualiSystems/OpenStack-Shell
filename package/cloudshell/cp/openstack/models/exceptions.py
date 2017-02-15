class CommandCancellationException(Exception):
    """
    This exception is raised when command is cancelled.
    """
    pass


class InstanceErrorStateException(Exception):
    """
    This exception is raised when instance state is ERROR.
    """
    pass
