"""Tests for the :mod:`bigchaindb.backend.rethinkdb.admin` module."""
import pytest

import rethinkdb as r


def _count_rethinkdb_servers():
    from bigchaindb import config
    conn = r.connect(host=config['database']['host'],
                     port=config['database']['port'])
    return len(list(r.db('rethinkdb').table('server_status').run(conn)))


@pytest.fixture
def rdb_conn(db_host, db_port, db_name):
    return r.connect(host=db_host, port=db_port, db=db_name)


@pytest.mark.bdb
def test_set_shards(rdb_conn, db_name, db_conn):
    from bigchaindb.backend.schema import TABLES
    from bigchaindb.backend.rethinkdb.admin import set_shards
    for table in TABLES:
        table_config = r.db(db_name).table('backlog').config().run(rdb_conn)
        assert len(table_config['shards']) == 1
    what_happened = set_shards(db_conn, shards=2)
    for table in TABLES:
        assert what_happened[table]['reconfigured'] == 1
        config_changes = what_happened[table]['config_changes']
        assert len(config_changes) == 1
        assert len(config_changes[0]['new_val']['shards']) == 2
        assert len(what_happened[table]['status_changes']) == 1
        status_change = what_happened[table]['status_changes'][0]
        assert not status_change['new_val']['status']['all_replicas_ready']
        table_config = r.db(db_name).table(table).config().run(rdb_conn)
        assert len(table_config['shards']) == 2


@pytest.mark.bdb
def test_set_shards_dry_run(rdb_conn, db_name, db_conn):
    from bigchaindb.backend.schema import TABLES
    from bigchaindb.backend.rethinkdb.admin import set_shards
    for table in TABLES:
        table_config = r.db(db_name).table('backlog').config().run(rdb_conn)
        assert len(table_config['shards']) == 1
    what_happened = set_shards(db_conn, shards=2, dry_run=True)
    for table in TABLES:
        assert what_happened[table]['reconfigured'] == 0
        config_changes = what_happened[table]['config_changes']
        assert len(config_changes) == 1
        assert len(config_changes[0]['new_val']['shards']) == 2
        assert 'status_change' not in what_happened[table]
        table_config = r.db(db_name).table(table).config().run(rdb_conn)
        assert len(table_config['shards']) == 1


@pytest.mark.bdb
@pytest.mark.skipif(
    _count_rethinkdb_servers() < 2,
    reason=('Requires at least two servers. It\'s impossible to have'
            'more replicas of the data than there are servers.')
)
def test_set_replicas(rdb_conn, db_name, db_conn):
    from bigchaindb.backend.schema import TABLES
    from bigchaindb.backend.rethinkdb.admin import set_replicas
    for table in TABLES:
        table_config = r.db(db_name).table(table).config().run(rdb_conn)
        replicas_before = table_config['shards'][0]['replicas']
        assert len(replicas_before) == 1
    what_happened = set_replicas(db_conn, replicas=2)
    for table in TABLES:
        assert what_happened[table]['reconfigured'] == 1
        config_changes = what_happened[table]['config_changes']
        assert len(config_changes) == 1
        assert len(config_changes[0]['new_val']['shards'][0]['replicas']) == 2
        assert len(what_happened[table]['status_changes']) == 1
        status_change = what_happened[table]['status_changes'][0]
        assert not status_change['new_val']['status']['all_replicas_ready']
        table_config = r.db(db_name).table(table).config().run(rdb_conn)
        assert len(table_config['shards'][0]['replicas']) == 2
        assert (table_config['shards'][0]['replicas'][0] !=
                table_config['shards'][0]['replicas'][1])


@pytest.mark.bdb
@pytest.mark.skipif(
    _count_rethinkdb_servers() < 2,
    reason=('Requires at least two servers. It\'s impossible to have'
            'more replicas of the data than there are servers.')
)
def test_set_replicas_dry_run(rdb_conn, db_name, db_conn):
    from bigchaindb.backend.schema import TABLES
    from bigchaindb.backend.rethinkdb.admin import set_replicas
    for table in TABLES:
        table_config = r.db(db_name).table(table).config().run(rdb_conn)
        replicas_before = table_config['shards'][0]['replicas']
        assert len(replicas_before) == 1
    what_happened = set_replicas(db_conn, replicas=2, dry_run=True)
    for table in TABLES:
        assert what_happened[table]['reconfigured'] == 0
        config_changes = what_happened[table]['config_changes']
        assert len(config_changes) == 1
        assert len(config_changes[0]['new_val']['shards'][0]['replicas']) == 2
        assert 'status_change' not in what_happened[table]
        table_config = r.db(db_name).table(table).config().run(rdb_conn)
        assert len(table_config['shards'][0]['replicas']) == 1


@pytest.mark.bdb
@pytest.mark.skipif(
    _count_rethinkdb_servers() < 2,
    reason=('Requires at least two servers. It\'s impossible to have'
            'more replicas of the data than there are servers.')
)
def test_reconfigure(rdb_conn, db_name, db_conn):
    from bigchaindb.backend.rethinkdb.admin import reconfigure
    table_config = r.db(db_name).table('backlog').config().run(rdb_conn)
    replicas_before = table_config['shards'][0]['replicas']
    assert len(replicas_before) == 1
    reconfigure(db_conn, table='backlog', shards=2, replicas=2)
    table_config = r.db(db_name).table('backlog').config().run(rdb_conn)
    assert len(table_config['shards'][0]['replicas']) == 2
    assert (table_config['shards'][0]['replicas'][0] !=
            table_config['shards'][0]['replicas'][1])


@pytest.mark.bdb
def test_reconfigure_shards_for_real(rdb_conn, db_name, db_conn):
    from bigchaindb.backend.rethinkdb.admin import reconfigure
    table_config = r.db(db_name).table('backlog').config().run(rdb_conn)
    replicas_before = table_config['shards'][0]['replicas']
    assert len(replicas_before) == 1
    assert len(table_config['shards']) == 1
    what_happened = reconfigure(
        db_conn,
        table='backlog',
        shards=2,
        replicas={'default': 1},
        primary_replica_tag='default',
        nonvoting_replica_tags=('default',),
    )
    assert what_happened['reconfigured'] == 1
    assert len(what_happened['config_changes']) == 1
    assert len(what_happened['config_changes'][0]['new_val']['shards']) == 2
    assert len(what_happened['status_changes']) == 1
    status_change = what_happened['status_changes'][0]
    assert not status_change['new_val']['status']['all_replicas_ready']
    table_config = r.db(db_name).table('backlog').config().run(rdb_conn)
    assert len(table_config['shards']) == 2


@pytest.mark.bdb
def test_reconfigure_shards_dry_run(rdb_conn, db_name, db_conn):
    from bigchaindb.backend.rethinkdb.admin import reconfigure
    table_config = r.db(db_name).table('backlog').config().run(rdb_conn)
    replicas_before = table_config['shards'][0]['replicas']
    assert len(replicas_before) == 1
    assert len(table_config['shards']) == 1
    what_happened = reconfigure(
        db_conn,
        table='backlog',
        shards=2,
        replicas={'default': 1},
        primary_replica_tag='default',
        nonvoting_replica_tags=('default',),
        dry_run=True,
    )
    assert what_happened['reconfigured'] == 0
    assert len(what_happened['config_changes']) == 1
    assert len(what_happened['config_changes'][0]['new_val']['shards']) == 2
    table_config = r.db(db_name).table('backlog').config().run(rdb_conn)
    assert len(table_config['shards']) == 1


@pytest.mark.bdb
def test_reconfigure_replicas_without_nonvoting_replica_tags(rdb_conn,
                                                             db_name,
                                                             db_conn):
    from bigchaindb.backend.rethinkdb.admin import reconfigure
    from bigchaindb.backend.exceptions import OperationError
    with pytest.raises(OperationError) as exc:
        reconfigure(db_conn, table='backlog', shards=1,
                    replicas={'default': 1}, primary_replica_tag='default')
    assert isinstance(exc.value.__cause__, r.ReqlQueryLogicError)


@pytest.mark.bdb
def test_reconfigure_too_many_replicas(rdb_conn, db_name, db_conn):
    from bigchaindb.backend.rethinkdb.admin import reconfigure
    from bigchaindb.backend.exceptions import OperationError
    replicas = _count_rethinkdb_servers() + 1
    with pytest.raises(OperationError) as exc:
        reconfigure(db_conn, table='backlog', shards=1, replicas=replicas)
    assert isinstance(exc.value.__cause__, r.ReqlOpFailedError)
