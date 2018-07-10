"""Database creation and schema-providing interfaces for backends.

Attributes:
    TABLES (tuple): The three standard tables BigchainDB relies on:

        * ``backlog`` for incoming transactions awaiting to be put into
          a block.
        * ``bigchain`` for blocks.

"""

from functools import singledispatch
import logging

import bigchaindb
from bigchaindb.backend.connection import connect
from bigchaindb.common.exceptions import ValidationError
from bigchaindb.common.utils import validate_all_values_for_key

logger = logging.getLogger(__name__)

TABLES = ('bigchain', 'backlog', 'assets', 'metadata')
VALID_LANGUAGES = ('danish', 'dutch', 'english', 'finnish', 'french', 'german',
                   'hungarian', 'italian', 'norwegian', 'portuguese', 'romanian',
                   'russian', 'spanish', 'swedish', 'turkish', 'none',
                   'da', 'nl', 'en', 'fi', 'fr', 'de', 'hu', 'it', 'nb', 'pt',
                   'ro', 'ru', 'es', 'sv', 'tr')


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


def validate_language_key(obj, key):
    """Validate all nested "language" key in `obj`.

       Args:
           obj (dict): dictionary whose "language" key is to be validated.

       Returns:
           None: validation successful

        Raises:
            ValidationError: will raise exception in case language is not valid.
    """
    backend = bigchaindb.config['database']['backend']

    if backend == 'localmongodb':
        data = obj.get(key, {})
        if isinstance(data, dict):
            validate_all_values_for_key(data, 'language', validate_language)


def validate_language(value):
    """Check if `value` is a valid language.
       https://docs.mongodb.com/manual/reference/text-search-languages/

        Args:
            value (str): language to validated

        Returns:
            None: validation successful

        Raises:
            ValidationError: will raise exception in case language is not valid.
    """
    if value not in VALID_LANGUAGES:
        error_str = ('MongoDB does not support text search for the '
                     'language "{}". If you do not understand this error '
                     'message then please rename key/field "language" to '
                     'something else like "lang".').format(value)
        raise ValidationError(error_str)
