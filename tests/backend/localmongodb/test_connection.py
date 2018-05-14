from unittest import mock

import pytest
import pymongo
from pymongo import MongoClient
from pymongo.database import Database


pytestmark = [pytest.mark.bdb, pytest.mark.tendermint]


@pytest.fixture
def mock_cmd_line_opts():
    return {'argv': ['mongod', '--dbpath=/data'],
            'ok': 1.0,
            'parsed': {'replication': {'replSet': None},
                       'storage': {'dbPath': '/data'}}}


@pytest.fixture
def mock_config_opts():
    return {'argv': ['mongod', '--dbpath=/data'],
            'ok': 1.0,
            'parsed': {'replication': {'replSetName': None},
                       'storage': {'dbPath': '/data'}}}


@pytest.fixture
def mongodb_connection():
    import bigchaindb
    return MongoClient(host=bigchaindb.config['database']['host'],
                       port=bigchaindb.config['database']['port'])


def test_get_connection_returns_the_correct_instance(db_host, db_port):
    from bigchaindb.backend import connect
    from bigchaindb.backend.connection import Connection
    from bigchaindb.backend.localmongodb.connection import LocalMongoDBConnection

    config = {
        'backend': 'localmongodb',
        'host': db_host,
        'port': db_port,
        'name': 'test',
        'replicaset': None,
    }

    conn = connect(**config)
    assert isinstance(conn, Connection)
    assert isinstance(conn, LocalMongoDBConnection)
    assert conn.conn._topology_settings.replica_set_name == config['replicaset']


@mock.patch('bigchaindb.backend.localmongodb.connection.initialize_replica_set')
@mock.patch('pymongo.MongoClient.__init__')
@mock.patch('time.sleep')
def test_connection_error(mock_sleep, mock_client, mock_init_repl_set):
    from bigchaindb.backend import connect
    from bigchaindb.backend.exceptions import ConnectionError

    # force the driver to throw ConnectionFailure
    # the mock on time.sleep is to prevent the actual sleep when running
    # the tests
    mock_client.side_effect = pymongo.errors.ConnectionFailure()

    with pytest.raises(ConnectionError):
        conn = connect()
        conn.db

    assert mock_client.call_count == 3


@mock.patch('bigchaindb.backend.localmongodb.connection.initialize_replica_set')
@mock.patch('pymongo.MongoClient')
def test_connection_run_errors(mock_client, mock_init_repl_set):
    from bigchaindb.backend import connect
    from bigchaindb.backend.exceptions import (DuplicateKeyError,
                                               OperationError,
                                               ConnectionError)

    conn = connect()

    query = mock.Mock()
    query.run.side_effect = pymongo.errors.AutoReconnect('foo')
    with pytest.raises(ConnectionError):
        conn.run(query)
    assert query.run.call_count == 2

    query = mock.Mock()
    query.run.side_effect = pymongo.errors.DuplicateKeyError('foo')
    with pytest.raises(DuplicateKeyError):
        conn.run(query)
    assert query.run.call_count == 1

    query = mock.Mock()
    query.run.side_effect = pymongo.errors.OperationFailure('foo')
    with pytest.raises(OperationError):
        conn.run(query)
    assert query.run.call_count == 1


@mock.patch('pymongo.database.Database.authenticate')
def test_connection_with_credentials(mock_authenticate):
    import bigchaindb
    from bigchaindb.backend.localmongodb.connection import LocalMongoDBConnection
    conn = LocalMongoDBConnection(host=bigchaindb.config['database']['host'],
                                  port=bigchaindb.config['database']['port'],
                                  login='theplague',
                                  password='secret')
    conn.connect()
    assert mock_authenticate.call_count == 1


def test_check_replica_set_not_enabled(mongodb_connection):
    from bigchaindb.backend.localmongodb.connection import _check_replica_set
    from bigchaindb.common.exceptions import ConfigurationError

    # no replSet option set
    cmd_line_opts = {'argv': ['mongod', '--dbpath=/data'],
                     'ok': 1.0,
                     'parsed': {'storage': {'dbPath': '/data'}}}
    with mock.patch.object(Database, 'command', return_value=cmd_line_opts):
        with pytest.raises(ConfigurationError):
            _check_replica_set(mongodb_connection)


def test_check_replica_set_command_line(mongodb_connection,
                                        mock_cmd_line_opts):
    from bigchaindb.backend.localmongodb.connection import _check_replica_set

    # replSet option set through the command line
    with mock.patch.object(Database, 'command',
                           return_value=mock_cmd_line_opts):
        assert _check_replica_set(mongodb_connection) is None


def test_check_replica_set_config_file(mongodb_connection, mock_config_opts):
    from bigchaindb.backend.localmongodb.connection import _check_replica_set

    # replSet option set through the config file
    with mock.patch.object(Database, 'command', return_value=mock_config_opts):
        assert _check_replica_set(mongodb_connection) is None


def test_check_replica_set_name_mismatch(mongodb_connection,
                                         mock_cmd_line_opts):
    from bigchaindb.backend.localmongodb.connection import _check_replica_set
    from bigchaindb.common.exceptions import ConfigurationError

    # change the replica set name so it does not match the bigchaindb config
    mock_cmd_line_opts['parsed']['replication']['replSet'] = 'rs0'

    with mock.patch.object(Database, 'command',
                           return_value=mock_cmd_line_opts):
        with pytest.raises(ConfigurationError):
            _check_replica_set(mongodb_connection)


def test_wait_for_replica_set_initialization(mongodb_connection):
    from bigchaindb.backend.localmongodb.connection import _wait_for_replica_set_initialization  # noqa

    with mock.patch.object(Database, 'command') as mock_command:
        mock_command.side_effect = [
            {'log': ['a line']},
            {'log': ['database writes are now permitted']},
        ]

        # check that it returns
        assert _wait_for_replica_set_initialization(mongodb_connection) is None


def test_initialize_replica_set(mock_cmd_line_opts):
    from bigchaindb.backend.localmongodb.connection import initialize_replica_set

    with mock.patch.object(Database, 'command') as mock_command:
        mock_command.side_effect = [
            mock_cmd_line_opts,
            None,
            {'log': ['database writes are now permitted']},
        ]

        # check that it returns
        assert initialize_replica_set('host', 1337, 1000, 'dbname', False, None, None,
                                      None, None, None, None, None) is None

    # test it raises OperationError if anything wrong
    with mock.patch.object(Database, 'command') as mock_command:
        mock_command.side_effect = [
            mock_cmd_line_opts,
            pymongo.errors.OperationFailure(None, details={'codeName': ''})
        ]

        with pytest.raises(pymongo.errors.OperationFailure):
            initialize_replica_set('host', 1337, 1000, 'dbname', False, None,
                                   None, None, None, None, None, None) is None
