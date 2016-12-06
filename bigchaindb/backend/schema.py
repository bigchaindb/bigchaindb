"""Schema-providing interfaces for backend databases"""

from functools import singledispatch


@singledispatch
def create_database(connection, name):
    """Create database to be used by BigchainDB

    Args:
        name (str): the name of the database to create.

    Raises:
        :exc:`~bigchaindb.common.exceptions.DatabaseAlreadyExists`: If the
        given :attr:`name` already exists as a database.
    """

    raise NotImplementedError


@singledispatch
def create_tables(connection, name):
    """Create the tables to be used by BigchainDB

    Args:
        name (str): the name of the database to create tables for.
    """

    raise NotImplementedError


@singledispatch
def create_indexes(connection, name):
    """Create the indexes to be used by BigchainDB

    Args:
        name (str): the name of the database to create indexes for.
    """

    raise NotImplementedError


@singledispatch
def drop_database(connection, name):
    """Drop the database used by BigchainDB

    Args:
        name (str): the name of the database to drop.

    Raises:
        :exc:`~bigchaindb.common.exceptions.DatabaseDoesNotExist`: If the
        given :attr:`name` does not exist as a database.
    """

    raise NotImplementedError
