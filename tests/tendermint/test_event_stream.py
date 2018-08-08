import json
import base64
from queue import Queue

from aiohttp import ClientSession
import pytest


@pytest.mark.tendermint
def test_process_event_new_block():
    from bigchaindb.event_stream import process_event

    event = '{"jsonrpc": "2.0", "id": "test_stream_id#event",  "result": {'\
            '"query": "tm.event=\'NewBlock\'", "data": { "type": "CF18EA939D3240",'\
            '"value": { "block": { "header": { "chain_id": "test-chain-ipQIAa",'\
            '"height": 1, "time": "2018-04-23T14:49:30.509920098Z", "num_txs": 1,'\
            '"last_block_id": { "hash": "", "parts": { "total": 0, "hash": "" }},'\
            '"total_txs": 1, "last_commit_hash": "", "data_hash": "38792142CE6D7F6F46F71777CB53F94CD9497B23",'\
            '"validators_hash": "BF0D0EC2E13C76E69FA572516B6D93E64F3C58EF",'\
            '"consensus_hash": "F66EF1DF8BA6DAC7A1ECCE40CC84E54A1CEBC6A5", "app_hash": "",'\
            '"last_results_hash": "", "evidence_hash": "" }, "data": {"txs": ['\
            '"eyJpbnB1dHMiOiBbeyJvd25lcnNfYmVmb3JlIjogWyJFb2Z0Z0FNd2hKQXM0cW81b'\
            '0dhOU1GWXF5dFp5WEdaNmVmZFVYc1dXTDdmZSJdLCAiZnVsZmlsbHMiOiBudWxsLCA'\
            'iZnVsZmlsbG1lbnQiOiAicEdTQUlNMGNueFFGeTZrSE1PcGxBbzh1ZncwNDlsZ2VxN'\
            'HBOeDFNdksya0pjRjBCZ1VETjN2RTlsWmhaT21jMWZHbFpLUFZmZDdCTi1RVTdBa0N'\
            'TZ1NKWVRPYzB3YVlmQ1RXc1FQS1VmOE5fODFKd21YOUJxcnlLejYyTmVubHg0dGszN'\
            'GtVRCJ9XSwgIm91dHB1dHMiOiBbeyJwdWJsaWNfa2V5cyI6IFsiRW9mdGdBTXdoSkF'\
            'zNHFvNW9HYTlNRllxeXRaeVhHWjZlZmRVWHNXV0w3ZmUiXSwgImNvbmRpdGlvbiI6I'\
            'HsiZGV0YWlscyI6IHsidHlwZSI6ICJlZDI1NTE5LXNoYS0yNTYiLCAicHVibGljX2t'\
            'leSI6ICJFb2Z0Z0FNd2hKQXM0cW81b0dhOU1GWXF5dFp5WEdaNmVmZFVYc1dXTDdmZ'\
            'SJ9LCAidXJpIjogIm5pOi8vL3NoYS0yNTY7cFJZWTJQQUE0S3dHd0dUNVQtUXRCQUY'\
            '0VWY1WG5JcVkxWmExVER0N0hMQT9mcHQ9ZWQyNTUxOS1zaGEtMjU2JmNvc3Q9MTMxM'\
            'DcyIn0sICJhbW91bnQiOiAiMSJ9XSwgIm9wZXJhdGlvbiI6ICJDUkVBVEUiLCAibWV'\
            '0YWRhdGEiOiBudWxsLCAiYXNzZXQiOiB7ImRhdGEiOiBudWxsfSwgInZlcnNpb24iO'\
            'iAiMi4wIiwgImlkIjogImUwMmM0ZWM3MmExYzUzMmJkNjUyNWZkNGMxODU3ZDhmN2E'\
            'wYWVkYTgyNGVjY2NhZGY4NTlmNzc0Zjc3ZTgwZGUifQ=="]}, "evidence": {'\
            '"evidence": null}, "last_commit": { "blockID": { "hash": "", "parts":'\
            '{"total": 0, "hash": ""} }, "precommits": null } } } } } }'

    event_queue = Queue()
    process_event(event_queue, event, 'test_stream_id')
    assert not event_queue.empty()
    block = event_queue.get()
    assert isinstance(block.data['height'], int)


@pytest.mark.tendermint
def test_process_event_empty_block():
    from bigchaindb.event_stream import process_event

    event = '{"jsonrpc": "2.0", "id": "bigchaindb_stream_1524555674#event",'\
            '"result": {"query": "tm.event=\'NewBlock\'", "data": {"type": '\
            '"CF18EA939D3240", "value": {"block": {"header": {"chain_id": '\
            '"test-chain-ipQIAa", "height": 1, "time": "2018-04-24T07:41:16.838038877Z",'\
            '"num_txs": 0, "last_block_id": {"hash": "", "parts": {"total": 0, "hash": ""}},'\
            '"total_txs": 0, "last_commit_hash": "", "data_hash": "", "validators_hash":'\
            '"BF0D0EC2E13C76E69FA572516B6D93E64F3C58EF", "consensus_hash": '\
            '"F66EF1DF8BA6DAC7A1ECCE40CC84E54A1CEBC6A5", "app_hash": "", '\
            '"last_results_hash": "", "evidence_hash": ""}, "data": {"txs": null},'\
            '"evidence": {"evidence": null}, "last_commit": {"blockID": {"hash": "", '\
            '"parts": {"total": 0, "hash": ""}}, "precommits": null}}}}}}'

    event_queue = Queue()
    process_event(event_queue, event, 'test_stream_id')
    assert event_queue.empty()


@pytest.mark.tendermint
def test_process_unknown_event():
    from bigchaindb.event_stream import process_event

    event = '{"jsonrpc": "2.0", "id": "test_stream_id#event",'\
            ' "result": { "query": "tm.event=\'UnknownEvent\'" }}'

    event_queue = Queue()
    process_event(event_queue, event, 'test_stream_id')
    assert event_queue.empty()


@pytest.mark.asyncio
@pytest.mark.abci
async def test_subscribe_events(tendermint_ws_url, b):
    from bigchaindb.event_stream import subscribe_events
    from bigchaindb.common.crypto import generate_key_pair
    from bigchaindb.models import Transaction

    session = ClientSession()
    ws = await session.ws_connect(tendermint_ws_url)
    stream_id = 'bigchaindb_stream_01'
    await subscribe_events(ws, stream_id)
    msg = await ws.receive()
    assert msg.data
    msg_data_dict = json.loads(msg.data)
    assert msg_data_dict['id'] == stream_id
    assert msg_data_dict['jsonrpc'] == '2.0'
    assert msg_data_dict['result'] == {}

    alice = generate_key_pair()
    tx = Transaction.create([alice.public_key],
                            [([alice.public_key], 1)],
                            asset=None)\
                    .sign([alice.private_key])

    b.post_transaction(tx, 'broadcast_tx_async')
    msg = await ws.receive()
    msg_data_dict = json.loads(msg.data)
    raw_txn = msg_data_dict['result']['data']['value']['block']['data']['txs'][0]
    transaction = json.loads(base64.b64decode(raw_txn).decode('utf8'))

    assert transaction == tx.to_dict()
