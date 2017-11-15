import json
import pytest


@pytest.mark.bdb
@pytest.mark.tapp
def test_app(b):
    from bigchaindb.tendermint import App
    from bigchaindb.tendermint.utils import calculate_hash
    from abci.server import ProtocolHandler
    from io import BytesIO
    import abci.types_pb2 as types
    from abci.wire import read_message
    from bigchaindb.common.crypto import generate_key_pair
    from bigchaindb.models import Transaction
    from abci.messages import to_request_deliver_tx, to_request_check_tx

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
    assert block0['hash'] == ''

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
    assert b.get_transaction(tx.id).id == tx.id

    new_block_txn_hash = calculate_hash([tx.id])

    r = types.Request()
    r.end_block.height = 1
    data = p.process('end_block', r)
    res, err = read_message(BytesIO(data), types.Response)
    assert res
    assert 'end_block' == res.WhichOneof("value")

    new_block_hash = calculate_hash([block0['hash'], new_block_txn_hash])

    data = p.process('commit', None)
    res, err = read_message(BytesIO(data), types.Response)
    assert res
    assert res.commit.code == 0
    assert res.commit.data == new_block_hash.encode('utf-8')

    block0 = b.get_latest_block()
    assert block0
    assert block0['height'] == 1
    assert block0['hash'] == new_block_hash
