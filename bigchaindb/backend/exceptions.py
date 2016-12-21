from bigchaindb.exceptions import BigchainDBError


class DatabaseOpFailedError(BigchainDBError):
    """Exception for database operation errors."""
