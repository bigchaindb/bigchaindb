import pytest


@pytest.fixture
def mock_queue(monkeypatch):

    class MockQueue:
        items = []

        def get(self):
            return self.items.pop()

        def put(self, item):
            self.items.append(item)

    mockqueue = MockQueue()

    monkeypatch.setattr('queue.Queue', lambda: mockqueue)
    return mockqueue


def test_transform_create(b, user_private_key, user_public_key):
    from bigchaindb import util

    tx = util.create_tx(user_public_key, user_public_key, None, 'CREATE')
    tx = util.transform_create(tx)
    tx = util.sign_tx(tx, b.me_private)

    assert tx['transaction']['current_owner'] == b.me
    assert tx['transaction']['new_owner'] == user_public_key
    assert util.verify_signature(tx)


def test_empty_pool_is_populated_with_instances(mock_queue):
    from bigchaindb import util

    pool = util.pool(lambda: 'hello', limit=4)

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



def test_pool_blocks_if_no_instances_available(mock_queue):
    from bigchaindb import util

    pool = util.pool(lambda: 'hello', limit=4)

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

