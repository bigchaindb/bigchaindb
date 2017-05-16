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


@pytest.mark.bdb
def test_block_election_status_uses_result_cache(b):
    with patch('bigchaindb.core.gen_timestamp') as gt:
        gt.return_value = 12
        b.insert_block_result('a', False)
    assert b.block_election_status({'id': 'a'}) == b.BLOCK_INVALID


@pytest.mark.bdb
def test_block_election_status_caches_result_valid(b):
    with patch.object(b, 'block_election') as block_election:
        block_election.return_value = {'status': b.BLOCK_VALID}
        assert b.block_election_status({'id': 'a'}) == b.BLOCK_VALID
        assert b.block_election_status({'id': 'a'}) == b.BLOCK_VALID
        assert block_election.call_count == 1
    assert b.get_block_result('a')['result'] is True


@pytest.mark.bdb
def test_block_election_status_caches_result_invalid(b):
    with patch.object(b, 'block_election') as block_election:
        block_election.return_value = {'status': b.BLOCK_INVALID}
        assert b.block_election_status({'id': 'a'}) == b.BLOCK_INVALID
        assert b.block_election_status({'id': 'a'}) == b.BLOCK_INVALID
        assert block_election.call_count == 1
    assert b.get_block_result('a')['result'] is False


@pytest.mark.bdb
def test_block_election_status_caches_result_undecided(b):
    with patch.object(b, 'block_election') as block_election:
        block_election.return_value = {'status': b.BLOCK_UNDECIDED}
        assert b.block_election_status({'id': 'a'}) == b.BLOCK_UNDECIDED
        assert b.block_election_status({'id': 'a'}) == b.BLOCK_UNDECIDED
        assert block_election.call_count == 2
    assert b.get_block_result('a') is None
