import pytest
import rethinkdb as r

import bigchaindb
from bigchaindb import backend
from bigchaindb.backend.rethinkdb import schema
from ..conftest import setup_database as _setup_database


# Since we are testing database initialization and database drop,
# we need to use the `setup_database` fixture on a function level
@pytest.fixture(scope='function', autouse=True)
def setup_database(request, node_config):
    _setup_database(request, node_config)


def test_init_creates_db_tables_and_indexes():
    conn = backend.connect()
    dbname = bigchaindb.config['database']['name']

    # The db is set up by fixtures so we need to remove it
    conn.run(r.db_drop(dbname))

    schema.create_database(conn, dbname)

    assert conn.run(r.db_list().contains(dbname)) is True

    assert conn.run(r.db(dbname).table_list().contains('backlog', 'bigchain')) is True

    assert conn.run(r.db(dbname).table('bigchain').index_list().contains(
        'block_timestamp')) is True

    assert conn.run(r.db(dbname).table('backlog').index_list().contains(
        'assignee__transaction_timestamp')) is True


def test_create_database():
    conn = backend.connect()
    dbname = bigchaindb.config['database']['name']

    # The db is set up by fixtures so we need to remove it
    # and recreate it just with one table
    conn.run(r.db_drop(dbname))
    schema.create_database(conn, dbname)
    assert conn.run(r.db_list().contains(dbname)) is True


def test_create_tables():
    conn = backend.connect()
    dbname = bigchaindb.config['database']['name']

    # The db is set up by fixtures so we need to remove it
    # and recreate it just with one table
    conn.run(r.db_drop(dbname))
    schema.create_database(conn, dbname)
    schema.create_tables(conn, dbname)

    assert conn.run(r.db(dbname).table_list().contains('bigchain')) is True
    assert conn.run(r.db(dbname).table_list().contains('backlog')) is True
    assert conn.run(r.db(dbname).table_list().contains('votes')) is True
    assert len(conn.run(r.db(dbname).table_list())) == 3


def test_create_bigchain_secondary_index():
    conn = backend.connect()
    dbname = bigchaindb.config['database']['name']

    # The db is set up by fixtures so we need to remove it
    # and recreate it just with one table
    conn.run(r.db_drop(dbname))
    schema.create_database(conn, dbname)
    schema.create_tables(conn, dbname)
    schema.create_bigchain_secondary_index(conn, dbname)

    # Bigchain table
    assert conn.run(r.db(dbname).table('bigchain').index_list().contains(
        'block_timestamp')) is True
    assert conn.run(r.db(dbname).table('bigchain').index_list().contains(
        'transaction_id')) is True
    assert conn.run(r.db(dbname).table('bigchain').index_list().contains(
        'metadata_id')) is True
    assert conn.run(r.db(dbname).table('bigchain').index_list().contains(
        'asset_id')) is True

    # Backlog table
    assert conn.run(r.db(dbname).table('backlog').index_list().contains(
        'assignee__transaction_timestamp')) is True

    # Votes table
    assert conn.run(r.db(dbname).table('votes').index_list().contains(
        'block_and_voter')) is True


def test_init_database_fails_if_db_exists():
    from bigchaindb.common import exceptions

    conn = backend.connect()
    dbname = bigchaindb.config['database']['name']

    # The db is set up by fixtures
    assert conn.run(r.db_list().contains(dbname)) is True

    with pytest.raises(exceptions.DatabaseAlreadyExists):
        schema.init_database()


def test_drop():
    conn = backend.connect()
    dbname = bigchaindb.config['database']['name']

    # The db is set up by fixtures
    assert conn.run(r.db_list().contains(dbname)) is True

    schema.drop_database(conn, dbname)
    assert conn.run(r.db_list().contains(dbname)) is False


def test_drop_non_existent_db_raises_an_error():
    from bigchaindb.common import exceptions

    conn = backend.connect()
    dbname = bigchaindb.config['database']['name']

    # The db is set up by fixtures
    assert conn.run(r.db_list().contains(dbname)) is True

    schema.drop_database(conn, dbname)

    with pytest.raises(exceptions.DatabaseDoesNotExist):
        schema.drop_database(conn, dbname)
