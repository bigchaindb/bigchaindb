# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

from pytest import mark, raises


@mark.parametrize('schema_func_name,args_qty', (
    ('create_database', 1),
    ('create_tables', 1),
    ('drop_database', 1),
))
def test_schema(schema_func_name, args_qty):
    from bigchaindb.backend import schema
    schema_func = getattr(schema, schema_func_name)
    with raises(NotImplementedError):
        schema_func(None, *range(args_qty))


@mark.parametrize('query_func_name,args_qty', (
    ('delete_transactions', 1),
    ('get_txids_filtered', 1),
    ('get_owned_ids', 1),
    ('get_block', 1),
    ('get_spent', 2),
    ('get_spending_transactions', 1),
    ('store_assets', 1),
    ('get_asset', 1),
    ('store_metadatas', 1),
    ('get_metadata', 1),
))
def test_query(query_func_name, args_qty):
    from bigchaindb.backend import query
    query_func = getattr(query, query_func_name)
    with raises(NotImplementedError):
        query_func(None, *range(args_qty))
