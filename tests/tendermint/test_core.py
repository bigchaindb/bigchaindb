import json
import pytest

from abci.types_pb2 import (
    RequestBeginBlock,
    RequestEndBlock
)

from bigchaindb.core import CodeTypeOk, CodeTypeError


pytestmark = [pytest.mark.tendermint, pytest.mark.bdb]


def encode_tx_to_bytes(transaction):
    return json.dumps(transaction.to_dict()).encode('utf8')


def test_check_tx__signed_create_is_ok(b):
    from bigchaindb import App
    from bigchaindb.models import Transaction
    from bigchaindb.common.crypto import generate_key_pair

    alice = generate_key_pair()
    bob = generate_key_pair()

    tx = Transaction.create([alice.public_key],
                            [([bob.public_key], 1)])\
                    .sign([alice.private_key])

    app = App(b)
    result = app.check_tx(encode_tx_to_bytes(tx))
    assert result.code == CodeTypeOk


def test_check_tx__unsigned_create_is_error(b):
    from bigchaindb import App
    from bigchaindb.models import Transaction
    from bigchaindb.common.crypto import generate_key_pair

    alice = generate_key_pair()
    bob = generate_key_pair()

    tx = Transaction.create([alice.public_key],
                            [([bob.public_key], 1)])

    app = App(b)
    result = app.check_tx(encode_tx_to_bytes(tx))
    assert result.code == CodeTypeError


@pytest.mark.bdb
def test_deliver_tx__valid_create_updates_db(b):
    from bigchaindb import App
    from bigchaindb.models import Transaction
    from bigchaindb.common.crypto import generate_key_pair

    alice = generate_key_pair()
    bob = generate_key_pair()

    tx = Transaction.create([alice.public_key],
                            [([bob.public_key], 1)])\
                    .sign([alice.private_key])

    app = App(b)

    begin_block = RequestBeginBlock()
    app.init_chain(['ignore'])
    app.begin_block(begin_block)

    result = app.deliver_tx(encode_tx_to_bytes(tx))
    assert result.code == CodeTypeOk

    app.end_block(RequestEndBlock(height=99))
    app.commit()
    assert b.get_transaction(tx.id).id == tx.id

    # unspent_outputs = b.get_unspent_outputs()
    # unspent_output = next(unspent_outputs)
    # expected_unspent_output = next(tx.unspent_outputs)._asdict()
    # assert unspent_output == expected_unspent_output
    # with pytest.raises(StopIteration):
    #     next(unspent_outputs)


def test_deliver_tx__double_spend_fails(b):
    from bigchaindb import App
    from bigchaindb.models import Transaction
    from bigchaindb.common.crypto import generate_key_pair

    alice = generate_key_pair()
    bob = generate_key_pair()

    tx = Transaction.create([alice.public_key],
                            [([bob.public_key], 1)])\
                    .sign([alice.private_key])

    app = App(b)
    app.init_chain(['ignore'])

    begin_block = RequestBeginBlock()
    app.begin_block(begin_block)

    result = app.deliver_tx(encode_tx_to_bytes(tx))
    assert result.code == CodeTypeOk

    app.end_block(RequestEndBlock(height=99))
    app.commit()

    assert b.get_transaction(tx.id).id == tx.id
    result = app.deliver_tx(encode_tx_to_bytes(tx))
    assert result.code == CodeTypeError


def test_deliver_transfer_tx__double_spend_fails(b):
    from bigchaindb import App
    from bigchaindb.models import Transaction
    from bigchaindb.common.crypto import generate_key_pair

    app = App(b)
    app.init_chain(['ignore'])

    begin_block = RequestBeginBlock()
    app.begin_block(begin_block)

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
    assert result.code == CodeTypeOk

    tx_transfer = Transaction.transfer(tx.to_inputs(),
                                       [([bob.public_key], 1)],
                                       asset_id=tx.id)\
                             .sign([alice.private_key])

    result = app.deliver_tx(encode_tx_to_bytes(tx_transfer))
    assert result.code == CodeTypeOk

    double_spend = Transaction.transfer(tx.to_inputs(),
                                        [([carly.public_key], 1)],
                                        asset_id=tx.id)\
                              .sign([alice.private_key])

    result = app.deliver_tx(encode_tx_to_bytes(double_spend))
    assert result.code == CodeTypeError


def test_end_block_return_validator_updates(b):
    from bigchaindb import App
    from bigchaindb.backend import query
    from bigchaindb.core import encode_validator
    from bigchaindb.backend.query import VALIDATOR_UPDATE_ID

    app = App(b)
    app.init_chain(['ignore'])

    begin_block = RequestBeginBlock()
    app.begin_block(begin_block)

    validator = {'pub_key': {'type': 'ed25519',
                             'data': 'B0E42D2589A455EAD339A035D6CE1C8C3E25863F268120AA0162AD7D003A4014'},
                 'power': 10}
    validator_update = {'validator': validator,
                        'update_id': VALIDATOR_UPDATE_ID}
    query.store_validator_update(b.connection, validator_update)

    resp = app.end_block(RequestEndBlock(height=99))
    assert resp.validator_updates[0] == encode_validator(validator)

    updates = b.get_validator_update()
    assert updates == []


def test_store_pre_commit_state_in_end_block(b, alice):
    from bigchaindb import App
    from bigchaindb.backend import query
    from bigchaindb.models import Transaction
    from bigchaindb.backend.query import PRE_COMMIT_ID

    tx = Transaction.create([alice.public_key],
                            [([alice.public_key], 1)],
                            asset={'msg': 'live long and prosper'})\
                    .sign([alice.private_key])

    app = App(b)
    app.init_chain(['ignore'])

    begin_block = RequestBeginBlock()
    app.begin_block(begin_block)
    app.deliver_tx(encode_tx_to_bytes(tx))
    app.end_block(RequestEndBlock(height=99))

    resp = query.get_pre_commit_state(b.connection, PRE_COMMIT_ID)
    assert resp['commit_id'] == PRE_COMMIT_ID
    assert resp['height'] == 99
    assert resp['transactions'] == [tx.id]

    app.begin_block(begin_block)
    app.deliver_tx(encode_tx_to_bytes(tx))
    app.end_block(RequestEndBlock(height=100))
    resp = query.get_pre_commit_state(b.connection, PRE_COMMIT_ID)
    assert resp['commit_id'] == PRE_COMMIT_ID
    assert resp['height'] == 100
    assert resp['transactions'] == [tx.id]
