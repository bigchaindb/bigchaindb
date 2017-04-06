import pytest
from unittest.mock import patch


@pytest.mark.bdb
def test_insert_block_result(b):
    with patch('bigchaindb.core.gen_timestamp') as gt:
        gt.return_value = 12
        b.insert_block_result('a', False)
        b.insert_block_result('b', True)
    assert b.get_block_result('a') == {
        'block_id': 'a',
        'result': False,
        'timestamp': 12,
    }
    assert b.get_block_result('b') == {
        'block_id': 'b',
        'result': True,
        'timestamp': 12,
    }


@pytest.mark.bdb
def test_get_block_result_nonexistant(b):
    assert b.get_block_result('cba') is None
