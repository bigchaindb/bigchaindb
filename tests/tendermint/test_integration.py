import json
from copy import deepcopy

import pytest
from abci.server import ProtocolHandler
from io import BytesIO
import abci.types_pb2 as types
from abci.encoding import read_message
from abci.messages import to_request_deliver_tx, to_request_check_tx


@pytest.mark.tendermint
@pytest.mark.bdb
def test_app(tb):
    from bigchaindb.tendermint import App
    from bigchaindb.tendermint.utils import calculate_hash
    from bigchaindb.common.crypto import generate_key_pair
    from bigchaindb.models import Transaction

    b = tb
    app = App(b)
    p = ProtocolHandler(app)

    data = p.process('info', None)
    res, err = read_message(BytesIO(data), types.Response)
    assert res
    assert res.info.last_block_app_hash == b''
    assert res.info.last_block_height == 0
    assert not b.get_latest_block()

    p.process('init_chain', None)
    block0 = b.get_latest_block()
    assert block0
    assert block0['height'] == 0
    assert block0['app_hash'] == ''

    alice = generate_key_pair()
    bob = generate_key_pair()
    tx = Transaction.create([alice.public_key],
                            [([bob.public_key], 1)])\
                    .sign([alice.private_key])
    etxn = json.dumps(tx.to_dict()).encode('utf8')

    r = to_request_check_tx(etxn)
    data = p.process('check_tx', r)
    res, err = read_message(BytesIO(data), types.Response)
    assert res
    assert res.check_tx.code == 0

    r = types.Request()
    r.begin_block.hash = b''
    p.process('begin_block', r)

    r = to_request_deliver_tx(etxn)
    data = p.process('deliver_tx', r)
    res, err = read_message(BytesIO(data), types.Response)
    assert res
    assert res.deliver_tx.code == 0

    new_block_txn_hash = calculate_hash([tx.id])

    r = types.Request()
    r.end_block.height = 1
    data = p.process('end_block', r)
    res, err = read_message(BytesIO(data), types.Response)
    assert res
    assert 'end_block' == res.WhichOneof('value')

    new_block_hash = calculate_hash([block0['app_hash'], new_block_txn_hash])

    data = p.process('commit', None)
    res, err = read_message(BytesIO(data), types.Response)
    assert res.commit.data == new_block_hash.encode('utf-8')
    assert b.get_transaction(tx.id).id == tx.id

    block0 = b.get_latest_block()
    assert block0
    assert block0['height'] == 1
    assert block0['app_hash'] == new_block_hash

    # empty block should not update height
    r = types.Request()
    r.begin_block.hash = new_block_hash.encode('utf-8')
    p.process('begin_block', r)

    r = types.Request()
    r.end_block.height = 2
    p.process('end_block', r)

    data = p.process('commit', None)
    res, err = read_message(BytesIO(data), types.Response)
    assert res.commit.data == new_block_hash.encode('utf-8')

    block0 = b.get_latest_block()
    assert block0
    assert block0['height'] == 1

    # when empty block is generated hash of previous block should be returned
    assert block0['app_hash'] == new_block_hash


@pytest.mark.skip(reason='Not working with Tendermint 0.19.0')
@pytest.mark.abci
def test_upsert_validator(b, alice):
    from bigchaindb.backend.query import VALIDATOR_UPDATE_ID
    from bigchaindb.backend import query, connect
    from bigchaindb.models import Transaction

    conn = connect()
    public_key = '1718D2DBFF00158A0852A17A01C78F4DCF3BA8E4FB7B8586807FAC182A535034'
    power = 1
    validator = {'pub_key': {'type': 'ed25519',
                             'data': public_key},
                 'power': power}
    validator_update = {'validator': validator,
                        'update_id': VALIDATOR_UPDATE_ID}

    query.store_validator_update(conn, deepcopy(validator_update))

    tx = Transaction.create([alice.public_key],
                            [([alice.public_key], 1)],
                            asset=None)\
                    .sign([alice.private_key])

    code, message = b.write_transaction(tx, 'broadcast_tx_commit')
    assert code == 202

    validators = b.get_validators()
    validators = [(v['pub_key']['data'], v['voting_power']) for v in validators]

    assert ((public_key, power) in validators)


@pytest.mark.abci
def test_post_transaction_responses(tendermint_ws_url, b):
    from bigchaindb.common.crypto import generate_key_pair
    from bigchaindb.models import Transaction

    alice = generate_key_pair()
    bob = generate_key_pair()
    tx = Transaction.create([alice.public_key],
                            [([alice.public_key], 1)],
                            asset=None)\
                    .sign([alice.private_key])

    code, message = b.write_transaction(tx, 'broadcast_tx_commit')
    assert code == 202

    tx_transfer = Transaction.transfer(tx.to_inputs(),
                                       [([bob.public_key], 1)],
                                       asset_id=tx.id)\
                             .sign([alice.private_key])

    code, message = b.write_transaction(tx_transfer, 'broadcast_tx_commit')
    assert code == 202

    # NOTE: DOESN'T WORK (double spend)
    # Tendermint crashes with error: Unexpected result type
    # carly = generate_key_pair()
    # double_spend = Transaction.transfer(tx.to_inputs(),
    #                                     [([carly.public_key], 1)],
    #                                     asset_id=tx.id)\
    #                           .sign([alice.private_key])
    # code, message = b.write_transaction(double_spend, 'broadcast_tx_commit')
    # assert code == 500
