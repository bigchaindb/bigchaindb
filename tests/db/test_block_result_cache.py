import pytest
from bigchaindb.backend import query
from unittest.mock import patch


@pytest.mark.bdb
def test_insert_block_result_first(b):
    with patch('bigchaindb.core.gen_timestamp') as gt:
        gt.return_value = 12
        b.insert_block_result('a', True)
    assert query.get_block_result(b.connection, 'a') == {
        'block_id': 'a',
        'result': True,
        'timestamp': 12,
    }


@pytest.mark.bdb
def test_insert_block_result_nonfirst(b):
    with patch('bigchaindb.core.gen_timestamp') as gt:
        gt.return_value = 12
        b.insert_block_result('a', True)
        b.insert_block_result('b', True)
    assert query.get_block_result(b.connection, 'b') == {
        'block_id': 'b',
        'result': True,
        'timestamp': 12,
    }
