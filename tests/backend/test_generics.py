from importlib import import_module
from unittest.mock import patch

from pytest import mark, raises


@mark.parametrize('schema_func_name,args_qty', (
    ('create_database', 1),
    ('create_tables', 1),
    ('create_indexes', 1),
    ('drop_database', 1),
))
def test_schema(schema_func_name, args_qty):
    from bigchaindb.backend import schema
    schema_func = getattr(schema, schema_func_name)
    with raises(NotImplementedError):
        schema_func(None, *range(args_qty))


@mark.parametrize('query_func_name,args_qty', (
    ('write_transaction', 1),
    ('count_blocks', 0),
    ('count_backlog', 0),
    ('get_genesis_block', 0),
    ('delete_transaction', 1),
    ('get_stale_transactions', 1),
    ('get_blocks_status_from_transaction', 1),
    ('get_transaction_from_backlog', 1),
    ('get_txids_by_asset_id', 1),
    ('get_asset_by_id', 1),
    ('get_owned_ids', 1),
    ('get_votes_by_block_id', 1),
    ('write_block', 1),
    ('get_block', 1),
    ('has_transaction', 1),
    ('write_vote', 1),
    ('get_last_voted_block', 1),
    ('get_unvoted_blocks', 1),
    ('get_spent', 2),
    ('get_votes_by_block_id_and_voter', 2),
    ('update_transaction', 2),
    ('get_transaction_from_block', 2),
))
def test_query(query_func_name, args_qty):
    from bigchaindb.backend import query
    query_func = getattr(query, query_func_name)
    with raises(NotImplementedError):
        query_func(None, *range(args_qty))


@mark.parametrize('db,conn_cls', (
    ('mongodb', 'MongoDBConnection'),
    ('rethinkdb', 'RethinkDBConnection'),
))
@patch('bigchaindb.backend.schema.create_indexes',
       autospec=True, return_value=None)
@patch('bigchaindb.backend.schema.create_tables',
       autospec=True, return_value=None)
@patch('bigchaindb.backend.schema.create_database',
       autospec=True, return_value=None)
def test_init_database(mock_create_database, mock_create_tables,
                       mock_create_indexes, db, conn_cls):
    from bigchaindb.backend.schema import init_database
    conn = getattr(
        import_module('bigchaindb.backend.{}.connection'.format(db)),
        conn_cls,
    )('host', 'port', 'dbname')
    init_database(connection=conn, dbname='mickeymouse')
    mock_create_database.assert_called_once_with(conn, 'mickeymouse')
    mock_create_tables.assert_called_once_with(conn, 'mickeymouse')
    mock_create_indexes.assert_called_once_with(conn, 'mickeymouse')
