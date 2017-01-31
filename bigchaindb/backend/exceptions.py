from bigchaindb.exceptions import BigchainDBError


class ConnectionError(BigchainDBError):
    """Exception raised when the connection to the DataBase fails."""


class DatabaseOpFailedError(BigchainDBError):
    """Exception for database operation errors."""
