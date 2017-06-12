from unittest import mock

import pytest
import pymongo
from pymongo import MongoClient
from pymongo.database import Database
from ssl import CERT_REQUIRED


pytestmark = pytest.mark.bdb_ssl


@pytest.fixture
def mock_ssl_cmd_line_opts(certs_dir):
    return {'argv': [
        'mongod',
        '--dbpath=/data',
        '--replSet=bigchain-rs',
        '--sslMode=requireSSL',
        '--sslAllowInvalidHostnames',
        '--sslCAFile=' + certs_dir + '/ca.crt',
        '--sslCRLFile=' + certs_dir + '/crl.pem',
        '--sslPEMKeyFile=' + certs_dir + '/test_mdb_ssl_cert_and_key.pem',
        '--sslPEMKeyPassword=""'
        ],
        'ok': 1.0,
        'parsed': {'replication': {'replSet': 'bigchain-rs'},
                   'storage': {'dbPath': '/data'}}
        }


@pytest.fixture
def mock_ssl_config_opts(certs_dir):
    return {'argv': [
        'mongod',
        '--dbpath=/data',
        '--replSet=bigchain-rs',
        '--sslMode=requireSSL',
        '--sslAllowInvalidHostnames',
        '--sslCAFile=' + certs_dir + '/ca.crt',
        '--sslCRLFile=' + certs_dir + '/crl.pem',
        '--sslPEMKeyFile=' + certs_dir + '/test_mdb_ssl_cert_and_key.pem',
        '--sslPEMKeyPassword=""'
        ],
        'ok': 1.0,
        'parsed': {'replication': {'replSetName': 'bigchain-rs'},
                   'storage': {'dbPath': '/data'}}
        }


@pytest.fixture
def mongodb_ssl_connection(certs_dir):
    import bigchaindb
    return MongoClient(host=bigchaindb.config['database']['host'],
                       port=bigchaindb.config['database']['port'],
                       serverselectiontimeoutms=bigchaindb.config['database']['connection_timeout'],
                       ssl=bigchaindb.config['database']['ssl'],
                       ssl_ca_certs=bigchaindb.config['database']['ca_cert'],
                       ssl_certfile=bigchaindb.config['database']['certfile'],
                       ssl_keyfile=bigchaindb.config['database']['keyfile'],
                       ssl_pem_passphrase=bigchaindb.config['database']['keyfile_passphrase'],
                       ssl_crlfile=bigchaindb.config['database']['crlfile'],
                       ssl_cert_reqs=CERT_REQUIRED)


def test_ssl_get_connection_returns_the_correct_instance(db_host, db_port, certs_dir):
    from bigchaindb.backend import connect
    from bigchaindb.backend.connection import Connection
    from bigchaindb.backend.mongodb.connection import MongoDBConnection

    config = {
        'backend': 'mongodb',
        'host': db_host,
        'port': db_port,
        'name': 'test',
        'replicaset': 'bigchain-rs',
        'ssl': True,
        'ca_cert':   certs_dir + '/ca.crt',
        'crlfile':   certs_dir + '/crl.pem',
        'certfile':  certs_dir + '/test_bdb_ssl.crt',
        'keyfile':   certs_dir + '/test_bdb_ssl.key',
        'keyfile_passphrase': ''
    }

    conn = connect(**config)
    assert isinstance(conn, Connection)
    assert isinstance(conn, MongoDBConnection)
    assert conn.conn._topology_settings.replica_set_name == config['replicaset']


@mock.patch('bigchaindb.backend.mongodb.connection.initialize_replica_set')
@mock.patch('pymongo.MongoClient.__init__')
@mock.patch('time.sleep')
def test_ssl_connection_error(mock_sleep, mock_client, mock_init_repl_set):
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


@mock.patch('bigchaindb.backend.mongodb.connection.initialize_replica_set')
@mock.patch('pymongo.MongoClient')
def test_ssl_connection_run_errors(mock_client, mock_init_repl_set):
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
def test_ssl_connection_with_credentials(mock_authenticate):
    import bigchaindb
    from bigchaindb.backend.mongodb.connection import MongoDBConnection

    conn = MongoDBConnection(host=bigchaindb.config['database']['host'],
                             port=bigchaindb.config['database']['port'],
                             login='theplague',
                             password='secret',
                             ssl=bigchaindb.config['database']['ssl'],
                             ssl_ca_certs=bigchaindb.config['database']['ca_cert'],
                             ssl_certfile=bigchaindb.config['database']['certfile'],
                             ssl_keyfile=bigchaindb.config['database']['keyfile'],
                             ssl_pem_passphrase=bigchaindb.config['database']['keyfile_passphrase'],
                             ssl_crlfile=bigchaindb.config['database']['crlfile'],
                             ssl_cert_reqs=CERT_REQUIRED)
    conn.connect()
    assert mock_authenticate.call_count == 2


def test_ssl_check_replica_set_not_enabled(mongodb_ssl_connection):
    from bigchaindb.backend.mongodb.connection import _check_replica_set
    from bigchaindb.common.exceptions import ConfigurationError

    # no replSet option set
    cmd_line_opts = {'argv': ['mongod', '--dbpath=/data'],
                     'ok': 1.0,
                     'parsed': {'storage': {'dbPath': '/data'}}}
    with mock.patch.object(Database, 'command', return_value=cmd_line_opts):
        with pytest.raises(ConfigurationError):
            _check_replica_set(mongodb_ssl_connection)


def test_ssl_check_replica_set_command_line(mongodb_ssl_connection,
                                            mock_ssl_cmd_line_opts):
    from bigchaindb.backend.mongodb.connection import _check_replica_set

    # replSet option set through the command line
    with mock.patch.object(Database, 'command',
                           return_value=mock_ssl_cmd_line_opts):
        assert _check_replica_set(mongodb_ssl_connection) is None


def test_ssl_check_replica_set_config_file(mongodb_ssl_connection,
                                           mock_ssl_config_opts):
    from bigchaindb.backend.mongodb.connection import _check_replica_set

    # replSet option set through the config file
    with mock.patch.object(Database,
                           'command',
                           return_value=mock_ssl_config_opts):
        assert _check_replica_set(mongodb_ssl_connection) is None


def test_ssl_check_replica_set_name_mismatch(mongodb_ssl_connection,
                                             mock_ssl_cmd_line_opts):
    from bigchaindb.backend.mongodb.connection import _check_replica_set
    from bigchaindb.common.exceptions import ConfigurationError

    # change the replica set name so it does not match the bigchaindb config
    mock_ssl_cmd_line_opts['parsed']['replication']['replSet'] = 'rs0'

    with mock.patch.object(Database, 'command',
                           return_value=mock_ssl_cmd_line_opts):
        with pytest.raises(ConfigurationError):
            _check_replica_set(mongodb_ssl_connection)


def test_ssl_wait_for_replica_set_initialization(mongodb_ssl_connection):
    from bigchaindb.backend.mongodb.connection import _wait_for_replica_set_initialization  # noqa

    with mock.patch.object(Database, 'command') as mock_command:
        mock_command.side_effect = [
            {'log': ['a line']},
            {'log': ['database writes are now permitted']},
        ]

        # check that it returns
        assert _wait_for_replica_set_initialization(mongodb_ssl_connection) is None


def test_ssl_initialize_replica_set(mock_ssl_cmd_line_opts, certs_dir):
    from bigchaindb.backend.mongodb.connection import initialize_replica_set

    with mock.patch.object(Database, 'command') as mock_command:
        mock_command.side_effect = [
            mock_ssl_cmd_line_opts,
            None,
            {'log': ['database writes are now permitted']},
        ]

        # check that it returns
        assert initialize_replica_set('host',
                                      1337,
                                      1000,
                                      'dbname',
                                      True,
                                      None,
                                      None,
                                      certs_dir + '/ca.crt',
                                      certs_dir + '/test_bdb_ssl.crt',
                                      certs_dir + '/test_bdb_ssl.key',
                                      '',
                                      certs_dir + '/crl.pem') is None

    # test it raises OperationError if anything wrong
    with mock.patch.object(Database, 'command') as mock_command:
        mock_command.side_effect = [
            mock_ssl_cmd_line_opts,
            pymongo.errors.OperationFailure(None, details={'codeName': ''})
        ]

        with pytest.raises(pymongo.errors.OperationFailure):
            initialize_replica_set('host',
                                   1337,
                                   1000,
                                   'dbname',
                                   True,
                                   None,
                                   None,
                                   certs_dir + '/ca.crt',
                                   certs_dir + '/test_bdb_ssl.crt',
                                   certs_dir + '/test_bdb_ssl.key',
                                   '',
                                   certs_dir + '/crl.pem') is None


def test_ssl_invalid_configuration(db_host, db_port, certs_dir):
    from bigchaindb.backend import connect
    from bigchaindb.common.exceptions import ConfigurationError

    config = {
        'backend': 'mongodb',
        'host': db_host,
        'port': db_port,
        'name': 'test',
        'replicaset': 'bigchain-rs',
        'ssl': False,
        'ca_cert':   certs_dir + '/ca.crt',
        'crlfile':   certs_dir + '/crl.pem',
        'certfile':  certs_dir + '/test_bdb_ssl.crt',
        'keyfile':   certs_dir + '/test_bdb_ssl.key',
        'keyfile_passphrase': ''
    }

    with pytest.raises(ConfigurationError):
        conn = connect(**config)
        assert conn.conn._topology_settings.replica_set_name == config['replicaset']


def test_ssl_connection_with_wrong_credentials():
    import bigchaindb
    from bigchaindb.backend.mongodb.connection import MongoDBConnection
    from bigchaindb.backend.exceptions import AuthenticationError

    conn = MongoDBConnection(host=bigchaindb.config['database']['host'],
                             port=bigchaindb.config['database']['port'],
                             login='my_login',
                             password='my_super_secret_password',
                             ssl=bigchaindb.config['database']['ssl'],
                             ssl_ca_certs=bigchaindb.config['database']['ca_cert'],
                             ssl_certfile=bigchaindb.config['database']['certfile'],
                             ssl_keyfile=bigchaindb.config['database']['keyfile'],
                             ssl_pem_passphrase=bigchaindb.config['database']['keyfile_passphrase'],
                             ssl_crlfile=bigchaindb.config['database']['crlfile'],
                             ssl_cert_reqs=CERT_REQUIRED)

    with pytest.raises(AuthenticationError):
        conn._connect()
