class ConnectionError(Exception):
    """Raised when there is a connection error when running a query."""


class Connection:

    def run(self):
        raise NotImplementedError()

    def connect(self):
        raise NotImplementedError()
