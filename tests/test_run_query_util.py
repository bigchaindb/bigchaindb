from threading import Thread
import pytest

import rethinkdb as r

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
    import rethinkdb as r

    def raise_exception(*args, **kwargs):
        raise r.ReqlDriverError('mock')

    conn = Connection()
    original_connect = r.connect
    r.connect = raise_exception

    def delayed_start():
        time.sleep(1)
        r.connect = original_connect

    thread = Thread(target=delayed_start)
    query = r.expr('1')
    thread.start()
    assert conn.run(query) == '1'


def test_changefeed_reconnects_when_connection_lost(monkeypatch):
    import time
    import multiprocessing as mp

    from bigchaindb import Bigchain
    from bigchaindb.pipelines.utils import ChangeFeed

    class MockConnection:
        tries = 0

        def run(self, *args, **kwargs):
            return self

        def __iter__(self):
            return self

        def __next__(self):
            self.tries += 1
            if self.tries == 1:
                raise r.ReqlDriverError('mock')
            elif self.tries == 2:
                return { 'new_val': { 'fact': 'A group of cats is called a clowder.' },
                         'old_val': None }
            if self.tries == 3:
                raise r.ReqlDriverError('mock')
            elif self.tries == 4:
                return { 'new_val': {'fact': 'Cats sleep 70% of their lives.' },
                         'old_val': None }
            else:
                time.sleep(10)


    bigchain = Bigchain()
    bigchain.connection = MockConnection()
    changefeed = ChangeFeed('cat_facts', ChangeFeed.INSERT,
                            bigchain=bigchain)
    changefeed.outqueue = mp.Queue()
    t_changefeed = Thread(target=changefeed.run_forever, daemon=True)

    t_changefeed.start()
    time.sleep(1)
    # try 1: MockConnection raises an error that will stop the
    #        ChangeFeed instance from iterating for 1 second.

    # try 2: MockConnection releases a new record. The new record
    #        will be put in the outqueue of the ChangeFeed instance.
    fact = changefeed.outqueue.get()['fact']
    assert fact == 'A group of cats is called a clowder.'

    # try 3: MockConnection raises an error that will stop the
    #        ChangeFeed instance from iterating for 1 second.
    assert t_changefeed.is_alive() is True

    time.sleep(2)
    # try 4: MockConnection releases a new record. The new record
    #        will be put in the outqueue of the ChangeFeed instance.

    fact = changefeed.outqueue.get()['fact']
    assert fact == 'Cats sleep 70% of their lives.'
