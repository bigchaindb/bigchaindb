import pytest
from bigchaindb.backend import query
from bigchaindb.common.crypto import hash_data
from unittest.mock import patch


@pytest.mark.bdb
def test_insert_block_result_first(b):
    with patch('bigchaindb.core.gen_timestamp') as gt:
        gt.return_value = 12
        b.insert_cached_block_result('a', True)
    assert query.get_cached_block_result(b.connection, 'a') == {
        'block_id': 'a',
        'chain_hash': hash_data('a'),
        'height': 0,
        'result': True,
        'timestamp': 12,
    }


@pytest.mark.bdb
def test_insert_block_result_nonfirst(b):
    with patch('bigchaindb.core.gen_timestamp') as gt:
        gt.return_value = 12
        b.insert_cached_block_result('a', True)
        b.insert_cached_block_result('b', True)
    assert query.get_cached_block_result(b.connection, 'b') == {
        'block_id': 'b',
        'chain_hash': hash_data(hash_data('a') + 'b'),
        'height': 1,
        'result': True,
        'timestamp': 12,
    }


@pytest.mark.bdb
def test_get_last_cached_block_result(b):
    with patch('bigchaindb.core.gen_timestamp') as gt:
        gt.return_value = 12
        b.insert_cached_block_result('c', True)
        b.insert_cached_block_result('b', True)
        b.insert_cached_block_result('a', True)
    assert query.get_last_cached_block_result(b.connection) == {
        'block_id': 'a',
        'chain_hash': hash_data(hash_data(hash_data('c') + 'b') + 'a'),
        'height': 2,
        'result': True,
        'timestamp': 12,
    }
