import pytest

from bigchaindb.common.transaction import TransactionLink

pytestmark = pytest.mark.bdb


def test_filter_valid_items(b, blockdata):
    blocks, _ = blockdata
    assert (b.fastquery.filter_valid_items(blocks, block_id_key=lambda b: b['id'])
            == [blocks[0], blocks[1]])


def test_get_outputs_by_public_key(b, user_pk, user2_pk, blockdata):
    blocks, _ = blockdata
    assert b.fastquery.get_outputs_by_public_key(user_pk) == [
            TransactionLink(blocks[1]['block']['transactions'][0]['id'], 0)
    ]
    assert b.fastquery.get_outputs_by_public_key(user2_pk) == [
            TransactionLink(blocks[0]['block']['transactions'][0]['id'], 0)
    ]
