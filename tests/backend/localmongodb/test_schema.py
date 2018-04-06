import pytest


pytestmark = [pytest.mark.bdb, pytest.mark.tendermint]


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
    assert set(collection_names) == {
        'transactions', 'assets', 'metadata', 'blocks', 'utxos', 'pre_commit',
        'validators'
    }

    indexes = conn.conn[dbname]['assets'].index_information().keys()
    assert set(indexes) == {'_id_', 'asset_id', 'text'}

    indexes = conn.conn[dbname]['transactions'].index_information().keys()
    assert set(indexes) == {
            '_id_', 'transaction_id', 'asset_id', 'outputs', 'inputs'}

    indexes = conn.conn[dbname]['blocks'].index_information().keys()
    assert set(indexes) == {'_id_', 'height'}

    indexes = conn.conn[dbname]['utxos'].index_information().keys()
    assert set(indexes) == {'_id_', 'utxo'}

    indexes = conn.conn[dbname]['pre_commit'].index_information().keys()
    assert set(indexes) == {'_id_', 'pre_commit_id'}

    indexes = conn.conn[dbname]['validators'].index_information().keys()
    assert set(indexes) == {'_id_', 'update_id'}


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
    assert set(collection_names) == {
        'transactions', 'assets', 'metadata', 'blocks', 'utxos', 'validators',
        'pre_commit'}


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

    indexes = conn.conn[dbname]['assets'].index_information().keys()
    assert set(indexes) == {'_id_', 'asset_id', 'text'}

    indexes = conn.conn[dbname]['transactions'].index_information().keys()
    assert set(indexes) == {
            '_id_', 'transaction_id', 'asset_id', 'outputs', 'inputs'}

    indexes = conn.conn[dbname]['blocks'].index_information().keys()
    assert set(indexes) == {'_id_', 'height'}

    index_info = conn.conn[dbname]['utxos'].index_information()
    assert set(index_info.keys()) == {'_id_', 'utxo'}
    assert index_info['utxo']['unique']
    assert index_info['utxo']['key'] == [('transaction_id', 1),
                                         ('output_index', 1)]

    indexes = conn.conn[dbname]['pre_commit'].index_information()
    assert set(indexes.keys()) == {'_id_', 'pre_commit_id'}
    assert indexes['pre_commit_id']['unique']


def test_drop(dummy_db):
    from bigchaindb import backend
    from bigchaindb.backend import schema

    conn = backend.connect()
    assert dummy_db in conn.conn.database_names()
    schema.drop_database(conn, dummy_db)
    assert dummy_db not in conn.conn.database_names()
