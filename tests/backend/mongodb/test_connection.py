from unittest import mock

import pytest
from pymongo.errors import ConnectionFailure


def test_get_connection_returns_the_correct_instance():
    from bigchaindb.backend import connect
    from bigchaindb.backend.connection import Connection
    from bigchaindb.backend.mongodb.connection import MongoDBConnection

    config = {
        'backend': 'mongodb',
        'host': 'localhost',
        'port': 27017,
        'name': 'test',
        'replicaset': 'bigchain-rs'
    }

    conn = connect(**config)
    assert isinstance(conn, Connection)
    assert isinstance(conn, MongoDBConnection)
    assert conn.conn._topology_settings.replica_set_name == config['replicaset']


@mock.patch('pymongo.MongoClient.__init__')
@mock.patch('time.sleep')
def test_connection_error(mock_sleep, mock_client):
    from bigchaindb.backend import connect

    # force the driver to trow ConnectionFailure
    # the mock on time.sleep is to prevent the actual sleep when running
    # the tests
    mock_client.side_effect = ConnectionFailure()

    with pytest.raises(ConnectionFailure):
        conn = connect()
        conn.db

    assert mock_client.call_count == 3
