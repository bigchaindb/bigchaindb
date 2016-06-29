"""Custom exceptions used in the `bigchaindb` package.
"""


class OperationError(Exception):
    """Raised when an operation cannot go through"""


class TransactionDoesNotExist(Exception):
    """Raised if the transaction is not in the database"""


class TransactionOwnerError(Exception):
    """Raised if a user tries to transfer a transaction they don't own"""


class DoubleSpend(Exception):
    """Raised if a double spend is found"""


class InvalidHash(Exception):
    """Raised if there was an error checking the hash for a particular operation"""


class InvalidSignature(Exception):
    """Raised if there was an error checking the signature for a particular operation"""


class DatabaseAlreadyExists(Exception):
    """Raised when trying to create the database but the db is already there"""


class DatabaseDoesNotExist(Exception):
    """Raised when trying to delete the database but the db is not there"""


class KeypairNotFoundException(Exception):
    """Raised if operation cannot proceed because the keypair was not given"""


class KeypairMismatchException(Exception):
    """Raised if the private key(s) provided for signing don't match any of the curret owner(s)"""


class StartupError(Exception):
    """Raised when there is an error starting up the system"""


class ImproperVoteError(Exception):
    """Raised when an invalid vote is found"""


class GenesisBlockAlreadyExistsError(Exception):
    """Raised when trying to create the already existing genesis block"""
