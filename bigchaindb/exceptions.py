class BigchainDBError(Exception):
    """Base class for BigchainDB exceptions."""


class CriticalDoubleSpend(BigchainDBError):
    """Data integrity error that requires attention"""
