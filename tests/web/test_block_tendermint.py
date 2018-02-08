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


@pytest.mark.bdb
def test_get_block_containing_transaction(tb, client):
    b = tb
    tx = Transaction.create([b.me], [([b.me], 1)], asset={'cycle': 'hero'})
    tx = tx.sign([b.me_private])
    b.store_transaction(tx)

    block = Block(app_hash='random_utxo',
                  height=13,
                  transactions=[tx.id])
    b.store_block(block._asdict())

    res = client.get('{}?transaction_id={}'.format(BLOCKS_ENDPOINT, tx.id))
    expected_response = [block.height]
    assert res.json == expected_response
    assert res.status_code == 200


@pytest.mark.bdb
def test_get_blocks_by_txid_endpoint_returns_empty_list_not_found(client):
    res = client.get(BLOCKS_ENDPOINT + '?transaction_id=')
    assert res.status_code == 200
    assert len(res.json) == 0

    res = client.get(BLOCKS_ENDPOINT + '?transaction_id=123')
    assert res.status_code == 200
    assert len(res.json) == 0


@pytest.mark.bdb
def test_get_blocks_by_txid_endpoint_returns_400_bad_query_params(client):
    res = client.get(BLOCKS_ENDPOINT)
    assert res.status_code == 400

    res = client.get(BLOCKS_ENDPOINT + '?ts_id=123')
    assert res.status_code == 400
    assert res.json == {
        'message': {
            'transaction_id': 'Missing required parameter in the JSON body or the post body or the query string'
        }
    }

    res = client.get(BLOCKS_ENDPOINT + '?transaction_id=123&foo=123')
    assert res.status_code == 400
    assert res.json == {
        'message': 'Unknown arguments: foo'
    }

    res = client.get(BLOCKS_ENDPOINT + '?transaction_id=123&status=123')
    assert res.status_code == 400
    assert res.json == {
        'message': 'Unknown arguments: status'
    }
