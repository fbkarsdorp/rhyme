
class ConnectionError(Exception):
    """
    Exception used to catch connection errors with the timbl server.
    """
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


class ServerConnectionError(ConnectionError):
    pass