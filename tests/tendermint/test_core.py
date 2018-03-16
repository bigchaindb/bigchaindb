import json

import pytest


pytestmark = [pytest.mark.tendermint, pytest.mark.bdb]


def encode_tx_to_bytes(transaction):
    return json.dumps(transaction.to_dict()).encode('utf8')


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


@pytest.mark.bdb
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
    app.init_chain(['ignore'])
    app.begin_block('ignore')

    result = app.deliver_tx(encode_tx_to_bytes(tx))
    assert result.is_ok()

    app.end_block(99)
    app.commit()
    assert b.get_transaction(tx.id).id == tx.id

    # unspent_outputs = b.get_unspent_outputs()
    # unspent_output = next(unspent_outputs)
    # expected_unspent_output = next(tx.unspent_outputs)._asdict()
    # assert unspent_output == expected_unspent_output
    # with pytest.raises(StopIteration):
    #     next(unspent_outputs)


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
    app.init_chain(['ignore'])
    app.begin_block('ignore')

    result = app.deliver_tx(encode_tx_to_bytes(tx))
    assert result.is_ok()

    app.end_block(99)
    app.commit()

    assert b.get_transaction(tx.id).id == tx.id
    result = app.deliver_tx(encode_tx_to_bytes(tx))
    assert result.is_error()


def test_deliver_transfer_tx__double_spend_fails(b):
    from bigchaindb.tendermint import App
    from bigchaindb.models import Transaction
    from bigchaindb.common.crypto import generate_key_pair

    app = App(b)
    app.init_chain(['ignore'])
    app.begin_block('ignore')

    alice = generate_key_pair()
    bob = generate_key_pair()
    carly = generate_key_pair()

    asset = {
        'msg': 'live long and prosper'
    }

    tx = Transaction.create([alice.public_key],
                            [([alice.public_key], 1)],
                            asset=asset)\
                    .sign([alice.private_key])

    result = app.deliver_tx(encode_tx_to_bytes(tx))
    assert result.is_ok()

    tx_transfer = Transaction.transfer(tx.to_inputs(),
                                       [([bob.public_key], 1)],
                                       asset_id=tx.id)\
                             .sign([alice.private_key])

    result = app.deliver_tx(encode_tx_to_bytes(tx_transfer))
    assert result.is_ok()

    double_spend = Transaction.transfer(tx.to_inputs(),
                                        [([carly.public_key], 1)],
                                        asset_id=tx.id)\
                              .sign([alice.private_key])

    result = app.deliver_tx(encode_tx_to_bytes(double_spend))
    assert result.is_error()
