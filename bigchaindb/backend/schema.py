"""Database creation and schema-providing interfaces for backends.

Attributes:
    TABLES (tuple): The three standard tables BigchainDB relies on:

        * ``backlog`` for incoming transactions awaiting to be put into
          a block.
        * ``bigchain`` for blocks.
        * ``votes`` to store votes for each block by each federation
          node.

"""

from functools import singledispatch
import logging

import bigchaindb
from bigchaindb.backend.connection import connect

logger = logging.getLogger(__name__)

TABLES = ('bigchain', 'backlog', 'votes')


@singledispatch
def create_database(connection, dbname):
    """Create database to be used by BigchainDB.

    Args:
        dbname (str): the name of the database to create.

    Raises:
        :exc:`~DatabaseAlreadyExists`: If the given :attr:`dbname` already
            exists as a database.
    """

    raise NotImplementedError


@singledispatch
def create_tables(connection, dbname):
    """Create the tables to be used by BigchainDB.

    Args:
        dbname (str): the name of the database to create tables for.
    """

    raise NotImplementedError


@singledispatch
def create_indexes(connection, dbname):
    """Create the indexes to be used by BigchainDB.

    Args:
        dbname (str): the name of the database to create indexes for.
    """

    raise NotImplementedError


@singledispatch
def drop_database(connection, dbname):
    """Drop the database used by BigchainDB.

    Args:
        dbname (str): the name of the database to drop.

    Raises:
        :exc:`~DatabaseDoesNotExist`: If the given :attr:`dbname` does not
            exist as a database.
    """

    raise NotImplementedError


def init_database(connection=None, dbname=None):
    """Initialize the configured backend for use with BigchainDB.

    Creates a database with :attr:`dbname` with any required tables
    and supporting indexes.

    Args:
        connection (:class:`~bigchaindb.backend.connection.Connection`): an
            existing connection to use to initialize the database.
            Creates one if not given.
        dbname (str): the name of the database to create.
            Defaults to the database name given in the BigchainDB
            configuration.

    Raises:
        :exc:`~DatabaseAlreadyExists`: If the given :attr:`dbname` already
            exists as a database.
    """

    connection = connection or connect()
    dbname = dbname or bigchaindb.config['database']['name']

    create_database(connection, dbname)
    create_tables(connection, dbname)
    create_indexes(connection, dbname)
