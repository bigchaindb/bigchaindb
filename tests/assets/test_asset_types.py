import json

from bigchaindb.common import crypto
from bigchaindb.common.exceptions import ValidationError
import pytest
import random

TX_ENDPOINT = '/api/v1/transactions/'


def post_tx(b, client, tx):
    class Response():
        status_code = None

    response = Response()
    try:
        b.validate_transaction(tx)
        response.status_code = 202
    except ValidationError:
        response.status_code = 400

    if response.status_code == 202:
        mine(b, [tx])
    return response


def mine(b, tx_list):
    block = b.create_block(tx_list)
    b.write_block(block)

    # vote the block valid
    vote = b.vote(block.id, b.get_last_voted_block().id, True)
    b.write_vote(vote)

    return block, vote


def create_simple_tx(user_pub, user_priv, asset=None, metadata=None):
    from bigchaindb.models import Transaction
    create_tx = Transaction.create([user_pub], [([user_pub], 1)], asset=asset, metadata=metadata)
    create_tx = create_tx.sign([user_priv])
    return create_tx


def transfer_simple_tx(user_pub, user_priv, input_tx, metadata=None):
    from bigchaindb.models import Transaction

    asset_id = input_tx.id if input_tx.operation == 'CREATE' else input_tx.asset['id']

    transfer_tx = Transaction.transfer(input_tx.to_inputs(),
                                       [([user_pub], 1)],
                                       asset_id=asset_id,
                                       metadata=metadata)
    transfer_tx = transfer_tx.sign([user_priv])

    return transfer_tx


@pytest.mark.bdb
@pytest.mark.usefixtures('inputs')
def test_asset_type_mix(b_consensus, client):
    from bigchaindb.models import Transaction

    alice_priv, alice_pub = crypto.generate_key_pair()

    create_a = create_simple_tx(
        alice_pub, alice_priv,
        asset={
            'type': 'mix',
            'data': {
                'material': 'secret sauce'
            }
        })
    response = post_tx(b_consensus, client, create_a)
    assert response.status_code == 202

    transfer_a = transfer_simple_tx(alice_pub, alice_priv, create_a)
    response = post_tx(b_consensus, client, transfer_a)
    assert response.status_code == 202

    bob_priv, bob_pub = crypto.generate_key_pair()
    tx_b = create_simple_tx(
        bob_pub,
        bob_priv,
        asset={
            'type': 'mix',
            'data': {
                'material': 'bulk'
            }
        })
    response = post_tx(b_consensus, client, tx_b)
    assert response.status_code == 202

    carly_priv, carly_pub = crypto.generate_key_pair()

    tx_mix = Transaction.transfer(
        transfer_a.to_inputs() + tx_b.to_inputs(),
        [([carly_pub], 1)],
        transfer_a.id
    )

    tx_mix_signed = tx_mix.sign([alice_priv, bob_priv])
    response = post_tx(b_consensus, client, tx_mix_signed)
    assert response.status_code == 202
