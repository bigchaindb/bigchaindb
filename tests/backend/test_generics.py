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
    ('get_txids_filtered', 1),
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


@mark.parametrize('changefeed_func_name,args_qty', (
    ('get_changefeed', 2),
))
def test_changefeed(changefeed_func_name, args_qty):
    from bigchaindb.backend import changefeed
    changefeed_func = getattr(changefeed, changefeed_func_name)
    with raises(NotImplementedError):
        changefeed_func(None, *range(args_qty))


@mark.parametrize('changefeed_class_func_name,args_qty', (
    ('run_forever', 0),
    ('run_changefeed', 0),
))
def test_changefeed_class(changefeed_class_func_name, args_qty):
    from bigchaindb.backend.changefeed import ChangeFeed
    changefeed_class_func = getattr(ChangeFeed, changefeed_class_func_name)
    with raises(NotImplementedError):
        changefeed_class_func(None, *range(args_qty))


@mark.parametrize('admin_func_name,kwargs', (
    ('get_config', {'table': None}),
    ('reconfigure', {'table': None, 'shards': None, 'replicas': None}),
    ('set_shards', {'shards': None}),
    ('set_replicas', {'replicas': None}),
))
def test_admin(admin_func_name, kwargs):
    from bigchaindb.backend import admin
    admin_func = getattr(admin, admin_func_name)
    with raises(NotImplementedError):
        admin_func(None, **kwargs)
