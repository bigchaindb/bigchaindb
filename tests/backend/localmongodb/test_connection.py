# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

from unittest import mock

import pytest
import pymongo
from pymongo import MongoClient


pytestmark = pytest.mark.bdb


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


@mock.patch('pymongo.MongoClient.__init__')
def test_connection_error(mock_client):
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


def test_connection_run_errors():
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
