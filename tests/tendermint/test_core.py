import json

import pytest


def encode_tx_to_bytes(transaction):
    return json.dumps(transaction.to_dict()).encode('utf8')


@pytest.mark.tendermint
def test_check_tx__signed_create_is_ok(b):
    from bigchaindb.tendermint import App
    from bigchaindb.models import Transaction
    from bigchaindb.common.crypto import generate_key_pair

    alice = generate_key_pair()
    bob = generate_key_pair()

    tx = Transaction.create([alice.public_key],
                            [([bob.public_key], 1)])\
                    .sign([alice.private_key])

    app = App(b)
    result = app.check_tx(encode_tx_to_bytes(tx))
    assert result.is_ok()


@pytest.mark.tendermint
def test_check_tx__unsigned_create_is_error(b):
    from bigchaindb.tendermint import App
    from bigchaindb.models import Transaction
    from bigchaindb.common.crypto import generate_key_pair

    alice = generate_key_pair()
    bob = generate_key_pair()

    tx = Transaction.create([alice.public_key],
                            [([bob.public_key], 1)])

    app = App(b)
    result = app.check_tx(encode_tx_to_bytes(tx))
    assert result.is_error()


@pytest.mark.tendermint
def test_deliver_tx__valid_create_updates_db(b):
    from bigchaindb.tendermint import App
    from bigchaindb.models import Transaction
    from bigchaindb.common.crypto import generate_key_pair

    alice = generate_key_pair()
    bob = generate_key_pair()

    tx = Transaction.create([alice.public_key],
                            [([bob.public_key], 1)])\
                    .sign([alice.private_key])

    app = App(b)
    result = app.deliver_tx(encode_tx_to_bytes(tx))
    assert result.is_ok()
    assert b.get_transaction(tx.id).id == tx.id


@pytest.mark.tendermint
def test_deliver_tx__double_spend_fails(b):
    from bigchaindb.tendermint import App
    from bigchaindb.models import Transaction
    from bigchaindb.common.crypto import generate_key_pair

    alice = generate_key_pair()
    bob = generate_key_pair()

    tx = Transaction.create([alice.public_key],
                            [([bob.public_key], 1)])\
                    .sign([alice.private_key])

    app = App(b)
    result = app.deliver_tx(encode_tx_to_bytes(tx))
    assert result.is_ok()
    assert b.get_transaction(tx.id).id == tx.id
    result = app.deliver_tx(encode_tx_to_bytes(tx))
    assert result.is_error()
