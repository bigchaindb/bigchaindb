from bigchaindb.exceptions import BigchainDBError


class BackendError(BigchainDBError):
    """Top level exception for any backend exception."""


class ConnectionError(BackendError):
    """Exception raised when the connection to the backend fails."""


class OperationError(BackendError):
    """Exception raised when a backend operation fails."""


class DuplicateKeyError(OperationError):
    """Exception raised when an insert fails because the key is not unique"""
