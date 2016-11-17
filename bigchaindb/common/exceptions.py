"""Custom exceptions used in the `bigchaindb` package.
"""


class ConfigurationError(Exception):
    """Raised when there is a problem with server configuration"""


class OperationError(Exception):
    """Raised when an operation cannot go through"""


class TransactionDoesNotExist(Exception):
    """Raised if the transaction is not in the database"""


class TransactionOwnerError(Exception):
    """Raised if a user tries to transfer a transaction they don't own"""


class DoubleSpend(Exception):
    """Raised if a double spend is found"""


class ValidationError(Exception):
    """Raised if there was an error in validation"""


class InvalidHash(ValidationError):
    """Raised if there was an error checking the hash for a particular
    operation"""


class SchemaValidationError(ValidationError):
    """Raised if there was any error validating an object's schema"""


class InvalidSignature(Exception):
    """Raised if there was an error checking the signature for a particular
    operation"""


class DatabaseAlreadyExists(Exception):
    """Raised when trying to create the database but the db is already there"""


class DatabaseDoesNotExist(Exception):
    """Raised when trying to delete the database but the db is not there"""


class KeypairNotFoundException(Exception):
    """Raised if operation cannot proceed because the keypair was not given"""


class KeypairMismatchException(Exception):
    """Raised if the private key(s) provided for signing don't match any of the
    current owner(s)"""


class StartupError(Exception):
    """Raised when there is an error starting up the system"""


class ImproperVoteError(Exception):
    """Raised if a vote is not constructed correctly, or signed incorrectly"""


class MultipleVotesError(Exception):
    """Raised if a voter has voted more than once"""


class GenesisBlockAlreadyExistsError(Exception):
    """Raised when trying to create the already existing genesis block"""


class CyclicBlockchainError(Exception):
    """Raised when there is a cycle in the blockchain"""


class TransactionNotInValidBlock(Exception):
    """Raised when a transfer transaction is attempting to fulfill the
    conditions of a transaction that is in an invalid or undecided block"""


class AssetIdMismatch(Exception):
    """Raised when multiple transaction inputs related to different assets"""


class AmountError(Exception):
    """Raised when the amount of a non-divisible asset is different then 1"""
