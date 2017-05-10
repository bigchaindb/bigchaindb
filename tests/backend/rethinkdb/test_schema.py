import pytest
import rethinkdb as r

import bigchaindb
from bigchaindb import backend
from bigchaindb.backend.rethinkdb import schema


@pytest.mark.bdb
def test_init_creates_db_tables_and_indexes():
    from bigchaindb.backend.schema import init_database
    conn = backend.connect()
    dbname = bigchaindb.config['database']['name']

    # The db is set up by fixtures so we need to remove it
    conn.run(r.db_drop(dbname))

    init_database()

    assert conn.run(r.db_list().contains(dbname)) is True

    assert conn.run(r.db(dbname).table_list().contains('backlog', 'bigchain')) is True

    assert conn.run(r.db(dbname).table('bigchain').index_list().contains(
        'block_timestamp')) is True

    assert conn.run(r.db(dbname).table('backlog').index_list().contains(
        'assignee__transaction_timestamp')) is True


@pytest.mark.bdb
def test_init_database_fails_if_db_exists():
    from bigchaindb.backend.schema import init_database
    from bigchaindb.common import exceptions

    conn = backend.connect()
    dbname = bigchaindb.config['database']['name']

    # The db is set up by fixtures
    assert conn.run(r.db_list().contains(dbname)) is True

    with pytest.raises(exceptions.DatabaseAlreadyExists):
        init_database()


def test_create_database(not_yet_created_db):
    conn = backend.connect()
    schema.create_database(conn, not_yet_created_db)
    assert conn.run(r.db_list().contains(not_yet_created_db)) is True


@pytest.mark.bdb
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
    assert conn.run(r.db(dbname).table_list().contains('assets')) is True
    assert len(conn.run(r.db(dbname).table_list())) == 4


@pytest.mark.bdb
def test_create_secondary_indexes():
    conn = backend.connect()
    dbname = bigchaindb.config['database']['name']

    # The db is set up by fixtures so we need to remove it
    # and recreate it just with one table
    conn.run(r.db_drop(dbname))
    schema.create_database(conn, dbname)
    schema.create_tables(conn, dbname)
    schema.create_indexes(conn, dbname)

    # Bigchain table
    assert conn.run(r.db(dbname).table('bigchain').index_list().contains(
        'block_timestamp')) is True
    assert conn.run(r.db(dbname).table('bigchain').index_list().contains(
        'transaction_id')) is True
    assert conn.run(r.db(dbname).table('bigchain').index_list().contains(
        'asset_id')) is True
    assert conn.run(r.db(dbname).table('bigchain').index_list().contains(
        'inputs')) is True
    assert conn.run(r.db(dbname).table('bigchain').index_list().contains(
        'outputs')) is True

    # Backlog table
    assert conn.run(r.db(dbname).table('backlog').index_list().contains(
        'assignee__transaction_timestamp')) is True

    # Votes table
    assert conn.run(r.db(dbname).table('votes').index_list().contains(
        'block_and_voter')) is True


def test_drop(dummy_db):
    conn = backend.connect()
    assert conn.run(r.db_list().contains(dummy_db)) is True
    schema.drop_database(conn, dummy_db)
    assert conn.run(r.db_list().contains(dummy_db)) is False


def test_drop_non_existent_db_raises_an_error(dummy_db):
    from bigchaindb.common import exceptions
    conn = backend.connect()
    assert conn.run(r.db_list().contains(dummy_db)) is True
    schema.drop_database(conn, dummy_db)
    with pytest.raises(exceptions.DatabaseDoesNotExist):
        schema.drop_database(conn, dummy_db)
