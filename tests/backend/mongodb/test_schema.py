import pytest
from unittest.mock import patch


@pytest.mark.usefixtures('setup_database')
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
    assert sorted(indexes) == ['_id_', 'assignee__transaction_timestamp']

    indexes = conn.conn[dbname]['votes'].index_information().keys()
    assert sorted(indexes) == ['_id_', 'block_and_voter']


@pytest.mark.usefixtures('setup_database')
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


@pytest.mark.usefixtures('setup_database')
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


@pytest.mark.usefixtures('setup_database')
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
    assert sorted(indexes) == ['_id_', 'assignee__transaction_timestamp']

    # Votes table
    indexes = conn.conn[dbname]['votes'].index_information().keys()
    assert sorted(indexes) == ['_id_', 'block_and_voter']


@pytest.mark.usefixtures('setup_database')
def test_drop():
    import bigchaindb
    from bigchaindb import backend
    from bigchaindb.backend import schema

    conn = backend.connect()
    dbname = bigchaindb.config['database']['name']

    # The db is set up by fixtures
    assert dbname in conn.conn.database_names()

    schema.drop_database(conn, dbname)
    assert dbname not in conn.conn.database_names()


@pytest.mark.usefixtures('setup_database')
def test_get_replica_set_name():
    from pymongo.database import Database
    from bigchaindb import backend
    from bigchaindb.backend.mongodb.schema import _get_replica_set_name
    from bigchaindb.common.exceptions import ConfigurationError

    conn = backend.connect()

    # no replSet option set
    cmd_line_opts = {'argv': ['mongod', '--dbpath=/data'],
                     'ok': 1.0,
                     'parsed': {'storage': {'dbPath': '/data'}}}
    with patch.object(Database, 'command', return_value=cmd_line_opts):
        with pytest.raises(ConfigurationError):
            _get_replica_set_name(conn)

    # replSet option set through the command line
    cmd_line_opts = {'argv': ['mongod', '--dbpath=/data', '--replSet=rs0'],
                     'ok': 1.0,
                     'parsed': {'replication': {'replSet': 'rs0'},
                                'storage': {'dbPath': '/data'}}}
    with patch.object(Database, 'command', return_value=cmd_line_opts):
        assert _get_replica_set_name(conn) == 'rs0'

    # replSet option set through the config file
    cmd_line_opts = {'argv': ['mongod', '--dbpath=/data', '--replSet=rs0'],
                     'ok': 1.0,
                     'parsed': {'replication': {'replSetName': 'rs0'},
                                'storage': {'dbPath': '/data'}}}
    with patch.object(Database, 'command', return_value=cmd_line_opts):
        assert _get_replica_set_name(conn) == 'rs0'
