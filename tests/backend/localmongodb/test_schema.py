# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0


def test_init_database_is_graceful_if_db_exists():
    import bigchaindb
    from bigchaindb import backend
    from bigchaindb.backend.schema import init_database

    conn = backend.connect()
    dbname = bigchaindb.config['database']['name']

    # The db is set up by the fixtures
    assert dbname in conn.conn.list_database_names()

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

    collection_names = conn.conn[dbname].list_collection_names()
    assert set(collection_names) == {
        'transactions', 'assets', 'metadata', 'blocks', 'utxos', 'validators', 'elections',
        'pre_commit', 'abci_chains',
    }

    indexes = conn.conn[dbname]['assets'].index_information().keys()
    assert set(indexes) == {'_id_', 'asset_id', 'text'}

    index_info = conn.conn[dbname]['transactions'].index_information()
    indexes = index_info.keys()
    assert set(indexes) == {
            '_id_', 'transaction_id', 'asset_id', 'outputs', 'inputs'}
    assert index_info['transaction_id']['unique']

    index_info = conn.conn[dbname]['blocks'].index_information()
    indexes = index_info.keys()
    assert set(indexes) == {'_id_', 'height'}
    assert index_info['height']['unique']

    index_info = conn.conn[dbname]['utxos'].index_information()
    assert set(index_info.keys()) == {'_id_', 'utxo'}
    assert index_info['utxo']['unique']
    assert index_info['utxo']['key'] == [('transaction_id', 1),
                                         ('output_index', 1)]

    indexes = conn.conn[dbname]['elections'].index_information()
    assert set(indexes.keys()) == {'_id_', 'election_id_height'}
    assert indexes['election_id_height']['unique']

    indexes = conn.conn[dbname]['pre_commit'].index_information()
    assert set(indexes.keys()) == {'_id_', 'height'}
    assert indexes['height']['unique']


def test_drop(dummy_db):
    from bigchaindb import backend
    from bigchaindb.backend import schema

    conn = backend.connect()
    assert dummy_db in conn.conn.list_database_names()
    schema.drop_database(conn, dummy_db)
    assert dummy_db not in conn.conn.list_database_names()
