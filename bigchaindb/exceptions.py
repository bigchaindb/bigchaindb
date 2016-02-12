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

