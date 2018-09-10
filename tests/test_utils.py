# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

import queue
from unittest.mock import patch, call

import pytest


@pytest.fixture
def mock_queue(monkeypatch):

    class MockQueue:
        items = []

        def get(self, timeout=None):
            try:
                return self.items.pop()
            except IndexError:
                if timeout:
                    raise queue.Empty()
                raise

        def put(self, item):
            self.items.append(item)

    mockqueue = MockQueue()

    monkeypatch.setattr('queue.Queue', lambda: mockqueue)
    return mockqueue


def test_empty_pool_is_populated_with_instances(mock_queue):
    from bigchaindb import utils

    pool = utils.pool(lambda: 'hello', 4)

    assert len(mock_queue.items) == 0

    with pool() as instance:
        assert instance == 'hello'
    assert len(mock_queue.items) == 1

    with pool() as instance:
        assert instance == 'hello'
    assert len(mock_queue.items) == 2

    with pool() as instance:
        assert instance == 'hello'
    assert len(mock_queue.items) == 3

    with pool() as instance:
        assert instance == 'hello'
    assert len(mock_queue.items) == 4

    with pool() as instance:
        assert instance == 'hello'
    assert len(mock_queue.items) == 4


def test_pool_blocks_if_no_instances_available(mock_queue):
    from bigchaindb import utils

    pool = utils.pool(lambda: 'hello', 4)

    assert len(mock_queue.items) == 0

    # We need to manually trigger the `__enter__` method so the context
    # manager will "hang" and not return the resource to the pool
    assert pool().__enter__() == 'hello'
    assert len(mock_queue.items) == 0

    assert pool().__enter__() == 'hello'
    assert len(mock_queue.items) == 0

    assert pool().__enter__() == 'hello'
    assert len(mock_queue.items) == 0

    # We need to keep a reference of the last context manager so we can
    # manually release the resource
    last = pool()
    assert last.__enter__() == 'hello'
    assert len(mock_queue.items) == 0

    # This would block using `queue.Queue` but since we mocked it it will
    # just raise a IndexError because it's trying to pop from an empty list.
    with pytest.raises(IndexError):
        assert pool().__enter__() == 'hello'
    assert len(mock_queue.items) == 0

    # Release the last resource
    last.__exit__(None, None, None)
    assert len(mock_queue.items) == 1

    assert pool().__enter__() == 'hello'
    assert len(mock_queue.items) == 0


def test_pool_raises_empty_exception_when_timeout(mock_queue):
    from bigchaindb import utils

    pool = utils.pool(lambda: 'hello', 1, timeout=1)

    assert len(mock_queue.items) == 0

    with pool() as instance:
        assert instance == 'hello'
    assert len(mock_queue.items) == 1

    # take the only resource available
    assert pool().__enter__() == 'hello'

    with pytest.raises(queue.Empty):
        with pool() as instance:
            assert instance == 'hello'


@patch('multiprocessing.Process')
def test_process_group_instantiates_and_start_processes(mock_process):
    from bigchaindb.utils import ProcessGroup

    def noop():
        pass

    concurrency = 10

    pg = ProcessGroup(concurrency=concurrency, group='test_group', target=noop)
    pg.start()

    mock_process.assert_has_calls([call(group='test_group', target=noop,
                                        name=None, args=(), kwargs={},
                                        daemon=None)
                                  for i in range(concurrency)], any_order=True)

    for process in pg.processes:
        process.start.assert_called_with()


def test_lazy_execution():
    from bigchaindb.utils import Lazy

    lz = Lazy()
    lz.split(',')[1].split(' ').pop(1).strip()
    result = lz.run('Like humans, cats tend to favor one paw over another')
    assert result == 'cats'

    class Cat:
        def __init__(self, name):
            self.name = name

    cat = Cat('Shmui')

    lz = Lazy()
    lz.name.upper()
    result = lz.run(cat)
    assert result == 'SHMUI'


def test_process_set_title():
    from uuid import uuid4
    from multiprocessing import Queue
    from setproctitle import getproctitle
    from bigchaindb.utils import Process

    queue = Queue()
    uuid = str(uuid4())

    process = Process(target=lambda: queue.put(getproctitle()),
                      name=uuid)
    process.start()
    assert queue.get() == uuid
