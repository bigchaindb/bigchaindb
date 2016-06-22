import queue
from unittest.mock import patch, call

import pytest

from cryptoconditions import ThresholdSha256Fulfillment


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


def test_transform_create(b, user_sk, user_vk):
    from bigchaindb import util
    tx = util.create_tx(user_vk, user_vk, None, 'CREATE')
    tx = util.transform_create(tx)
    tx = util.sign_tx(tx, b.me_private)

    assert tx['transaction']['fulfillments'][0]['current_owners'][0] == b.me
    assert tx['transaction']['conditions'][0]['new_owners'][0] == user_vk
    assert util.validate_fulfillments(tx)


def test_empty_pool_is_populated_with_instances(mock_queue):
    from bigchaindb import util

    pool = util.pool(lambda: 'hello', 4)

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
    from bigchaindb import util

    pool = util.pool(lambda: 'hello', 4)

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
    from bigchaindb import util

    pool = util.pool(lambda: 'hello', 1, timeout=1)

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
    from bigchaindb.util import ProcessGroup

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


def test_create_tx_with_empty_inputs():
    from bigchaindb.util import create_tx
    tx = create_tx(None, None, [], None)
    assert 'id' in tx
    assert 'transaction' in tx
    assert 'version' in tx
    assert 'fulfillments' in tx['transaction']
    assert 'conditions' in tx['transaction']
    assert 'operation' in tx['transaction']
    assert 'timestamp' in tx['transaction']
    assert 'data' in tx['transaction']
    assert len(tx['transaction']['fulfillments']) == 1
    assert tx['transaction']['fulfillments'][0] == {
        'current_owners': [], 'input': None, 'fulfillment': None, 'fid': 0}


def test_fulfill_threshold_signature_fulfillment_pubkey_notfound(monkeypatch):
    from bigchaindb.exceptions import KeypairMismatchException
    from bigchaindb.util import fulfill_threshold_signature_fulfillment
    monkeypatch.setattr(
        ThresholdSha256Fulfillment,
        'get_subcondition_from_vk',
        lambda x, y: []
    )
    fulfillment = {'current_owners': (None,)}
    parsed_fulfillment = ThresholdSha256Fulfillment()
    with pytest.raises(KeypairMismatchException):
        fulfill_threshold_signature_fulfillment(
            fulfillment, parsed_fulfillment, None, None)


def test_fulfill_threshold_signature_fulfillment_wrong_privkeys(monkeypatch):
    from bigchaindb.exceptions import KeypairMismatchException
    from bigchaindb.util import fulfill_threshold_signature_fulfillment
    monkeypatch.setattr(
        ThresholdSha256Fulfillment,
        'get_subcondition_from_vk',
        lambda x, y: (None,)
    )
    fulfillment = {'current_owners': ('alice-pub-key',)}
    parsed_fulfillment = ThresholdSha256Fulfillment()
    with pytest.raises(KeypairMismatchException):
        fulfill_threshold_signature_fulfillment(
            fulfillment, parsed_fulfillment, None, {})


def test_check_hash_and_signature_invalid_hash(monkeypatch):
    from bigchaindb.exceptions import InvalidHash
    from bigchaindb.util import check_hash_and_signature
    transaction = {'id': 'txid'}
    monkeypatch.setattr('bigchaindb.util.get_hash_data', lambda tx: 'txhash')
    with pytest.raises(InvalidHash):
        check_hash_and_signature(transaction)


def test_check_hash_and_signature_invalid_signature(monkeypatch):
    from bigchaindb.exceptions import InvalidSignature
    from bigchaindb.util import check_hash_and_signature
    transaction = {'id': 'txid'}
    monkeypatch.setattr('bigchaindb.util.get_hash_data', lambda tx: 'txid')
    monkeypatch.setattr(
        'bigchaindb.util.validate_fulfillments', lambda tx: False)
    with pytest.raises(InvalidSignature):
        check_hash_and_signature(transaction)
