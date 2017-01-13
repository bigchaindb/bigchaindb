from unittest import mock

import pytest
from pymongo.database import Database
from pymongo.errors import OperationFailure


pytestmark = pytest.mark.bdb


def test_init_creates_db_tables_and_indexes():
    import bigchaindb
    from bigchaindb import backend
    from bigchaindb.backend.schema import init_database

    conn = backend.connect()
    dbname = bigchaindb.config['database']['name']

    # the db is set up by the fixture so we need to remove it
    conn.conn.drop_database(dbname)

    init_database()

    collection_names = conn.conn[dbname].collection_names()
    assert sorted(collection_names) == ['backlog', 'bigchain', 'votes']

    indexes = conn.conn[dbname]['bigchain'].index_information().keys()
    assert sorted(indexes) == ['_id_', 'asset_id', 'block_timestamp',
                               'transaction_id']

    indexes = conn.conn[dbname]['backlog'].index_information().keys()
    assert sorted(indexes) == ['_id_', 'assignee__transaction_timestamp',
                               'transaction_id']

    indexes = conn.conn[dbname]['votes'].index_information().keys()
    assert sorted(indexes) == ['_id_', 'block_and_voter']


def test_init_database_fails_if_db_exists():
    import bigchaindb
    from bigchaindb import backend
    from bigchaindb.backend.schema import init_database
    from bigchaindb.common import exceptions

    conn = backend.connect()
    dbname = bigchaindb.config['database']['name']

    # The db is set up by the fixtures
    assert dbname in conn.conn.database_names()

    with pytest.raises(exceptions.DatabaseAlreadyExists):
        init_database()


def test_create_tables():
    import bigchaindb
    from bigchaindb import backend
    from bigchaindb.backend import schema

    conn = backend.connect()
    dbname = bigchaindb.config['database']['name']

    # The db is set up by the fixtures so we need to remove it
    conn.conn.drop_database(dbname)
    schema.create_database(conn, dbname)
    schema.create_tables(conn, dbname)

    collection_names = conn.conn[dbname].collection_names()
    assert sorted(collection_names) == ['backlog', 'bigchain', 'votes']


def test_create_secondary_indexes():
    import bigchaindb
    from bigchaindb import backend
    from bigchaindb.backend import schema

    conn = backend.connect()
    dbname = bigchaindb.config['database']['name']

    # The db is set up by the fixtures so we need to remove it
    conn.conn.drop_database(dbname)
    schema.create_database(conn, dbname)
    schema.create_tables(conn, dbname)
    schema.create_indexes(conn, dbname)

    # Bigchain table
    indexes = conn.conn[dbname]['bigchain'].index_information().keys()
    assert sorted(indexes) == ['_id_', 'asset_id', 'block_timestamp',
                               'transaction_id']

    # Backlog table
    indexes = conn.conn[dbname]['backlog'].index_information().keys()
    assert sorted(indexes) == ['_id_', 'assignee__transaction_timestamp',
                               'transaction_id']

    # Votes table
    indexes = conn.conn[dbname]['votes'].index_information().keys()
    assert sorted(indexes) == ['_id_', 'block_and_voter']


def test_drop(dummy_db):
    from bigchaindb import backend
    from bigchaindb.backend import schema

    conn = backend.connect()
    assert dummy_db in conn.conn.database_names()
    schema.drop_database(conn, dummy_db)
    assert dummy_db not in conn.conn.database_names()


def test_get_replica_set_name_not_enabled():
    from bigchaindb import backend
    from bigchaindb.backend.mongodb.schema import _get_replica_set_name
    from bigchaindb.common.exceptions import ConfigurationError

    conn = backend.connect()

    # no replSet option set
    cmd_line_opts = {'argv': ['mongod', '--dbpath=/data'],
                     'ok': 1.0,
                     'parsed': {'storage': {'dbPath': '/data'}}}
    with mock.patch.object(Database, 'command', return_value=cmd_line_opts):
        with pytest.raises(ConfigurationError):
            _get_replica_set_name(conn)


def test_get_replica_set_name_command_line():
    from bigchaindb import backend
    from bigchaindb.backend.mongodb.schema import _get_replica_set_name

    conn = backend.connect()

    # replSet option set through the command line
    cmd_line_opts = {'argv': ['mongod', '--dbpath=/data', '--replSet=rs0'],
                     'ok': 1.0,
                     'parsed': {'replication': {'replSet': 'rs0'},
                                'storage': {'dbPath': '/data'}}}
    with mock.patch.object(Database, 'command', return_value=cmd_line_opts):
        assert _get_replica_set_name(conn) == 'rs0'


def test_get_replica_set_name_config_file():
    from bigchaindb import backend
    from bigchaindb.backend.mongodb.schema import _get_replica_set_name

    conn = backend.connect()

    # replSet option set through the config file
    cmd_line_opts = {'argv': ['mongod', '--dbpath=/data', '--replSet=rs0'],
                     'ok': 1.0,
                     'parsed': {'replication': {'replSetName': 'rs0'},
                                'storage': {'dbPath': '/data'}}}
    with mock.patch.object(Database, 'command', return_value=cmd_line_opts):
        assert _get_replica_set_name(conn) == 'rs0'


def test_wait_for_replica_set_initialization():
    from bigchaindb.backend.mongodb.schema import _wait_for_replica_set_initialization  # noqa
    from bigchaindb.backend import connect
    conn = connect()

    with mock.patch.object(Database, 'command') as mock_command:
        mock_command.side_effect = [
            {'log': ['a line']},
            {'log': ['database writes are now permitted']},
        ]

        # check that it returns
        assert _wait_for_replica_set_initialization(conn) is None


def test_initialize_replica_set():
    from bigchaindb.backend.mongodb.schema import initialize_replica_set
    from bigchaindb.backend import connect
    conn = connect()

    with mock.patch.object(Database, 'command') as mock_command:
        mock_command.side_effect = [
            mock.DEFAULT,
            None,
            {'log': ['database writes are now permitted']},
        ]

        # check that it returns
        assert initialize_replica_set(conn) is None

    # test it raises OperationError if anything wrong
    with mock.patch.object(Database, 'command') as mock_command:
        mock_command.side_effect = [
            mock.DEFAULT,
            OperationFailure(None, details={'codeName': ''})
        ]

        with pytest.raises(OperationFailure):
            initialize_replica_set(conn)
