import pytest

from bigchaindb.common import crypto


def post_tx(b, client, tx):
    import json
    response = client.post('/api/v1/transactions/', data=json.dumps(tx.to_dict()))
    if response.status_code == 202:
        mine(b, [tx])
    return response


def list_outputs(b, client, user_pub):
    response = client.get('/api/v1/outputs/?public_key={}'.format(user_pub))
    return response


def create_simple_tx(user_pub, user_priv, asset=None, metadata=None):
    from bigchaindb.models import Transaction
    create_tx = Transaction.create([user_pub], [([user_pub], 1)], asset=asset, metadata=metadata)
    create_tx = create_tx.sign([user_priv])
    return create_tx


def transfer_simple_tx(user_pub, user_priv, input_tx, metadata=None):
    from bigchaindb.models import Transaction
    if input_tx.operation == 'CREATE':
        asset_id = input_tx.id
    else:
        asset_id = input_tx.asset['id']

    transfer_tx = Transaction.transfer(input_tx.to_inputs(),
                                       [([user_pub], 1)],
                                       asset_id=asset_id,
                                       metadata=metadata)
    transfer_tx = transfer_tx.sign([user_priv])
    return transfer_tx


def mine(b, tx_list):
    block = b.create_block(tx_list)
    b.write_block(block)

    # vote the block valid
    vote = b.vote(block.id, b.get_last_voted_block().id, True)
    b.write_vote(vote)

    return block, vote


def create_script(b, client, user_pub, user_priv, script):
    create_tx = create_simple_tx(user_pub, user_priv, asset={'script': script})
    response = post_tx(b, client, create_tx)
    return create_tx, response


def transfer_script(b, client, user_pub, user_priv, input_tx, metadata=None):
    transfer_tx = transfer_simple_tx(user_pub, user_priv, input_tx, metadata=metadata)
    response = post_tx(b, client, transfer_tx)
    return transfer_tx, response


@pytest.mark.bdb
@pytest.mark.usefixtures('inputs')
def test_asset_script_query_outputs(b, client):
    user_priv, user_pub = crypto.generate_key_pair()

    # balance == 0
    # balance < 1 should raise
    script = "if len(bigchain.get_outputs_filtered('{}', True)) == 0: raise".format(user_pub)
    create_tx, response = create_script(b, client, user_pub, user_priv, script=script)
    assert response.status_code == 400

    tx = create_simple_tx(user_pub, user_priv)
    mine(b, [tx])
    # balance == 1
    create_tx, response = create_script(b, client, user_pub, user_priv, script=script)
    assert response.status_code == 202
    # balance == 2
    _, response = transfer_script(b, client, user_pub, user_priv, create_tx)
    assert response.status_code == 202
    # balance == 3
    script = "if len(bigchain.get_outputs_filtered('{}', True)) != 3 : raise".format(user_pub)
    _, response = create_script(b, client, user_pub, user_priv, script=script)
    assert response.status_code == 202


@pytest.mark.bdb
@pytest.mark.usefixtures('inputs')
def test_asset_scripts_that_should_fail(b, client, user_pk):
    user_priv, user_pub = crypto.generate_key_pair()
    input_tx = b.get_owned_ids(user_pk).pop()

    scripts_that_should_fail = [
        "while(True): pass",
        "import sys; print(sys.path)",
        "if True: raise",
        "bigchain.delete_transaction({})".format(input_tx)
    ]

    for script in scripts_that_should_fail:
        create_tx, response = create_script(b, client, user_pub, user_priv, script=script)
        assert response.status_code == 400


@pytest.mark.bdb
@pytest.mark.usefixtures('inputs')
def test_asset_script_self_outputs(b, client):
    user_priv, user_pub = crypto.generate_key_pair()

    # always make sure that outputs[0] involves user_pub
    script = "if '{}' not in self.outputs[0].public_keys: raise".format(user_pub)
    create_tx, response = create_script(b, client, user_pub, user_priv, script=script)
    assert response.status_code == 202
    # transfer to user_pub
    transfer_tx, response = transfer_script(b, client, user_pub, user_priv, input_tx=create_tx)
    assert response.status_code == 202
    # fail: transfer to user_priv
    _, response = transfer_script(b, client, user_priv, user_priv, input_tx=transfer_tx)
    assert response.status_code == 400


@pytest.mark.bdb
@pytest.mark.usefixtures('inputs')
def test_asset_script_self_operation(b, client):
    user_priv, user_pub = crypto.generate_key_pair()

    script = "if self.operation != 'CREATE': raise"
    create_tx, response = create_script(b, client, user_pub, user_priv, script=script)
    assert response.status_code == 202
    transfer_tx, response = transfer_script(b, client, user_pub, user_priv, input_tx=create_tx)
    assert response.status_code == 400

    script = "if self.operation not in ['CREATE', 'TRANSFER']: raise"
    create_tx, response = create_script(b, client, user_pub, user_priv, script=script)
    assert response.status_code == 202
    transfer_tx, response = transfer_script(b, client, user_pub, user_priv, input_tx=create_tx)
    assert response.status_code == 202


@pytest.mark.bdb
@pytest.mark.usefixtures('inputs')
def test_asset_script_query_transactions(b, client):
    alice_priv, alice_pub = crypto.generate_key_pair()
    bob_priv, bob_pub = crypto.generate_key_pair()

    proof_tx = create_simple_tx(bob_pub, bob_priv)

    script = "if not bigchain.get_transaction('{}'): raise".format(proof_tx.id)
    create_tx, response = create_script(b, client, alice_pub, alice_priv, script=script)
    assert response.status_code == 400

    response = post_tx(b, client, proof_tx)
    assert response.status_code == 202

    create_tx, response = create_script(b, client, alice_pub, alice_priv, script=script)
    assert response.status_code == 202

    transfer_tx, response = transfer_script(b, client, bob_pub, alice_priv, input_tx=create_tx)
    assert response.status_code == 202


SCRIPT_EXCHANGE = """
# counterparty wants to sell the asset to someone
# I want to make sure that there is something on hold for me
counterparty = '{}'
me = '{}'
if self.operation == 'TRANSFER' and counterparty in self.inputs[0].owners_before:
    # get all my outputs
    inputs = []
    for output in bigchain.get_outputs_filtered(me, True):
        tx = bigchain.get_transaction(output.txid)
        inputs += tx.inputs[0].owners_before
    # check if me ever received from counterparty
    if not counterparty in inputs:
        raise
"""


@pytest.mark.bdb
@pytest.mark.usefixtures('inputs')
def test_asset_script_exchange(b, client):
    alice_priv, alice_pub = crypto.generate_key_pair()
    bob_priv, bob_pub = crypto.generate_key_pair()
    carly_priv, carly_pub = crypto.generate_key_pair()

    # alice: 0 - bob: 0 - carly: 0
    create_tx_alice = create_simple_tx(alice_pub, alice_priv,
                                       asset={'script': SCRIPT_EXCHANGE.format(bob_pub, alice_pub)})
    response = post_tx(b, client, create_tx_alice)
    assert response.status_code == 202
    # alice: 1 - bob: 0 - carly: 0

    transfer_tx_alice_bob, response = transfer_script(b, client, bob_pub, alice_priv, input_tx=create_tx_alice)
    assert response.status_code == 202
    # alice: 0 - bob: 1 - carly: 0

    transfer_tx_bob_carly, response = transfer_script(b, client, carly_pub, bob_priv, input_tx=transfer_tx_alice_bob)
    assert response.status_code == 400

    create_tx_bob = create_simple_tx(bob_pub, bob_priv,
                                     asset={'script': SCRIPT_EXCHANGE.format(alice_pub, bob_pub)})
    response = post_tx(b, client, create_tx_bob)
    assert response.status_code == 202
    # alice: 0 - bob: 2 - carly: 0

    transfer_tx_bob_alice, response = transfer_script(b, client, alice_pub, bob_priv, input_tx=transfer_tx_alice_bob)
    assert response.status_code == 400

    settling_tx_bob_alice, response = transfer_script(b, client, alice_pub, bob_priv, input_tx=create_tx_bob)
    assert response.status_code == 202
    # alice: 1 - bob: 1 - carly: 0

    transfer_tx_bob_carly, response = transfer_script(b, client, carly_pub, bob_priv, input_tx=transfer_tx_alice_bob)
    assert response.status_code == 202
    # alice: 1 - bob: 0 - carly: 1

    settling_tx_alice_carly, response = transfer_script(b, client, carly_pub, alice_priv,
                                                        input_tx=settling_tx_bob_alice)
    assert response.status_code == 202
    # alice: 0 - bob: 0 - carly: 2


SCRIPT_METADATA_STREAM = """
value = self.metadata['value']
if value > 0:
    raise
"""


@pytest.mark.bdb
@pytest.mark.usefixtures('inputs')
def test_asset_script_metadata_stream(b, client):
    stream_priv, stream_pub = crypto.generate_key_pair()

    metadata = {'value': 0}
    create_tx_stream = create_simple_tx(stream_pub, stream_priv,
                                        asset={'script': SCRIPT_METADATA_STREAM},
                                        metadata=metadata)

    response = post_tx(b, client, create_tx_stream)
    assert response.status_code == 202

    transfer_tx_stream, response = transfer_script(b, client, stream_pub, stream_priv,
                                                   input_tx=create_tx_stream,
                                                   metadata=metadata)
    assert response.status_code == 202

    transfer_tx_stream, response = transfer_script(b, client, stream_pub, stream_priv,
                                                   input_tx=transfer_tx_stream,
                                                   metadata={'value': 1})
    assert response.status_code == 400


SCRIPT_METADATA_STREAM_AND_INPUT_TX = """
value = self.metadata['value']
if self.operation == 'TRANSFER':
    input_tx = bigchain.get_transaction(self.inputs[0].fulfills.txid)
    if 'value' in input_tx.metadata:
        prev_value = input_tx.metadata['value']
        # trigger an event on increasing value
        if value > prev_value:
            raise
"""


@pytest.mark.bdb
@pytest.mark.usefixtures('inputs')
def test_asset_script_metadata_stream_and_input(b, client):
    stream_priv, stream_pub = crypto.generate_key_pair()

    metadata = {'value': 0}
    create_tx_stream = create_simple_tx(stream_pub, stream_priv,
                                        asset={'script': SCRIPT_METADATA_STREAM_AND_INPUT_TX},
                                        metadata=metadata)

    response = post_tx(b, client, create_tx_stream)
    assert response.status_code == 202

    transfer_tx_stream, response = transfer_script(b, client, stream_pub, stream_priv,
                                                   input_tx=create_tx_stream,
                                                   metadata=metadata)
    assert response.status_code == 202

    transfer_tx_stream, response = transfer_script(b, client, stream_pub, stream_priv,
                                                   input_tx=transfer_tx_stream,
                                                   metadata={'value': -1})
    assert response.status_code == 202

    transfer_tx_stream, response = transfer_script(b, client, stream_pub, stream_priv,
                                                   input_tx=transfer_tx_stream,
                                                   metadata={'value': 1})
    assert response.status_code == 400