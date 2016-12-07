"""Schema-providing interfaces for backend databases"""

from functools import singledispatch

import bigchaindb
from bigchaindb.backend.connection import connect


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


def init_database(conn=None, name=None):
    """Initialize the configured backend for use with BigchainDB.

    Creates a database with :attr:`name` with any required tables
    and supporting indexes.

    Args:
        conn (:class:`~bigchaindb.backend.connection.Connection`): an existing
            connection to use to initialize the database.
            Creates one if not given.
        name (str): the name of the database to create.
            Defaults to the name in the BigchainDB configuration.

    Raises:
        :exc:`~bigchaindb.common.exceptions.DatabaseAlreadyExists`: If the
        given :attr:`name` already exists as a database.
    """

    conn = conn or connect()
    name = name or bigchaindb.config['database']['name']

    create_database(conn, name)
    create_tables(conn, name)
    create_indexes(conn, name)
