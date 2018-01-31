import pytest

from bigchaindb.models import Transaction
from bigchaindb.tendermint.lib import Block

BLOCKS_ENDPOINT = '/api/v1/blocks/'

pytestmark = pytest.mark.tendermint


@pytest.mark.bdb
@pytest.mark.usefixtures('inputs')
def test_get_block_endpoint(tb, client):
    b = tb
    tx = Transaction.create([b.me], [([b.me], 1)], asset={'cycle': 'hero'})
    tx = tx.sign([b.me_private])
    b.store_transaction(tx)

    block = Block(app_hash='random_utxo',
                  height=31,
                  transactions=[tx.id])
    b.store_block(block._asdict())

    res = client.get(BLOCKS_ENDPOINT + str(block.height))
    expected_response = {'height': block.height, 'transactions': [tx.to_dict()]}
    assert res.json == expected_response
    assert res.status_code == 200


@pytest.mark.bdb
@pytest.mark.usefixtures('inputs')
def test_get_block_returns_404_if_not_found(client):
    res = client.get(BLOCKS_ENDPOINT + '123')
    assert res.status_code == 404

    res = client.get(BLOCKS_ENDPOINT + '123/')
    assert res.status_code == 404
