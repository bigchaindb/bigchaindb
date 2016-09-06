from threading import Thread
import pytest

import rethinkdb as r

from bigchaindb.commands.utils import start_temp_rethinkdb
from bigchaindb.db.utils import Connection


def test_run_a_simple_query():
    conn = Connection()
    query = r.expr('1')
    assert conn.run(query) == '1'


def test_raise_exception_when_max_tries():
    class MockQuery:
        def run(self, conn):
            raise r.ReqlDriverError('mock')

    conn = Connection()

    with pytest.raises(r.ReqlDriverError):
        conn.run(MockQuery())


def test_reconnect_when_connection_lost():
    import time

    proc = None

    def delayed_start():
        nonlocal proc
        time.sleep(1)
        proc, _ = start_temp_rethinkdb(38015)

    thread = Thread(target=delayed_start)
    conn = Connection(port=38015)
    query = r.expr('1')
    thread.start()
    assert conn.run(query) == '1'
    proc.terminate()
    proc.wait()


def test_changefeed_reconnects_when_connection_lost(monkeypatch):
    import os
    import time
    import tempfile
    import multiprocessing as mp

    import bigchaindb
    from bigchaindb.pipelines.utils import ChangeFeed

    dbport = 38015
    dbname = 'test_' + str(os.getpid())
    directory = tempfile.mkdtemp()

    monkeypatch.setitem(bigchaindb.config, 'database', {
        'host': 'localhost',
        'port': dbport,
        'name': dbname
    })

    proc, _ = start_temp_rethinkdb(dbport, directory=directory)

    # prepare DB and table
    conn = r.connect(port=dbport)
    r.db_create(dbname).run(conn)
    r.db(dbname).table_create('cat_facts').run(conn)

    # initialize ChangeFeed and put it in a thread
    changefeed = ChangeFeed('cat_facts', ChangeFeed.INSERT)
    changefeed.outqueue = mp.Queue()
    t_changefeed = Thread(target=changefeed.run_forever, daemon=True)

    t_changefeed.start()
    time.sleep(1)

    # insert some records in the table to start generating
    # events that changefeed will put in `outqueue`
    r.db(dbname).table('cat_facts').insert({
        'fact': 'A group of cats is called a clowder.'
    }).run(conn)

    # the event should be in the outqueue
    fact = changefeed.outqueue.get()['fact']
    assert fact == 'A group of cats is called a clowder.'

    # stop the DB process
    proc.terminate()
    proc.wait()

    assert t_changefeed.is_alive() is True

    proc, _ = start_temp_rethinkdb(dbport, directory=directory)

    time.sleep(2)

    conn = r.connect(port=dbport)
    r.db(dbname).table('cat_facts').insert({
        'fact': 'Cats sleep 70% of their lives.'
    }).run(conn)

    fact = changefeed.outqueue.get()['fact']
    assert fact == 'Cats sleep 70% of their lives.'

    # stop the DB process
    proc.terminate()
    proc.wait()
