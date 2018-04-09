import json
from queue import Queue

from aiohttp import ClientSession
import pytest


pytestmark = pytest.mark.tendermint


def test_process_event_new_block():
    from bigchaindb.tendermint.event_stream import process_event

    event = '{"id": "test_stream_id#event", "jsonrpc": "2.0", "result":'\
            ' {"data": {"data": {"block": {"data": {"txs": ["eyJpbnB1dHMiOiBb'\
            'eyJvd25lcnNfYmVmb3JlIjogWyJCWnZLQmNSUmgyd0tOOGZuTENlZUczSGhFaWF4'\
            'TWdyWmlib0gyeUZvYzVwTCJdLCAiZnVsZmlsbHMiOiBudWxsLCAiZnVsZmlsbG1l'\
            'bnQiOiAicEdTQUlKMER2S2JBeXkyQ2hqT212ZWVCc0FxWktTS0k3VDNWZGhtUkI2'\
            'V2dhdzdoZ1VDUHluUnFuQW9RWDh2UlNXeXNwYk5uYWVBaVpOU19lQ3V6ejhDZWtJ'\
            'OHBIejJnekExeDJkOF93NTUzWFVOUGJFbnpBUzhncURqeDFkaE1JeDM1ZnpVTCJ9'\
            'XSwgIm91dHB1dHMiOiBbeyJwdWJsaWNfa2V5cyI6IFsiQlp2S0JjUlJoMndLTjhm'\
            'bkxDZWVHM0hoRWlheE1nclppYm9IMnlGb2M1cEwiXSwgImNvbmRpdGlvbiI6IHsi'\
            'ZGV0YWlscyI6IHsidHlwZSI6ICJlZDI1NTE5LXNoYS0yNTYiLCAicHVibGljX2tl'\
            'eSI6ICJCWnZLQmNSUmgyd0tOOGZuTENlZUczSGhFaWF4TWdyWmlib0gyeUZvYzVw'\
            'TCJ9LCAidXJpIjogIm5pOi8vL3NoYS0yNTY7eHVFX1ZPNjd6aHc0LTRjN0k1YUtm'\
            'WGtzX1Q1MjUwMnBuOC1mcVJQQkloRT9mcHQ9ZWQyNTUxOS1zaGEtMjU2JmNvc3Q9'\
            'MTMxMDcyIn0sICJhbW91bnQiOiAiMSJ9XSwgIm9wZXJhdGlvbiI6ICJDUkVBVEUi'\
            'LCAibWV0YWRhdGEiOiB7InNob3J0IjogImxpdHRsZSJ9LCAiYXNzZXQiOiB7ImRh'\
            'dGEiOiB7ImJpY3ljbGUiOiB7InNlcmlhbF9udW1iZXIiOiAiYWJjZDEyMzQiLCAi'\
            'bWFudWZhY3R1cmVyIjogImJrZmFiIn19fSwgInZlcnNpb24iOiAiMS4wIiwgImlk'\
            'IjogIjE4NzM3Yzc0OWQxZGE2Yzc5YjFmYWZiZjkwOTkwNzEwMDA1ZWM4MTYxNGQ5'\
            'YWFiNDkyZTgwYTkzNWRkYThjMzAifQ=="]}, "header": {"height": 1}}},'\
            ' "type": "new_block"}, "name": "NewBlock"}}'

    event_queue = Queue()
    process_event(event_queue, event, 'test_stream_id')
    assert not event_queue.empty()
    block = event_queue.get()
    assert isinstance(block.data['height'], int)


def test_process_event_empty_block():
    from bigchaindb.tendermint.event_stream import process_event

    event = '{"jsonrpc": "2.0", "id": "test_stream_id#event",'\
            '"result": {"name": "NewBlock", "data": {"type": "new_block",'\
            ' "data": {"block": {"header": {"chain_id": "test-chain-cbVRwC",'\
            ' "height": 1, "time": "2017-12-04T22:42:54.33+05:30", "num_txs": 0,'\
            ' "last_block_id": {"hash": "", "parts": {"total": 0, "hash": ""}},'\
            ' "last_commit_hash": "", "data_hash": "",'\
            ' "validators_hash": "ACF23A690EB72D051931E878E8F3D6E01A17A81C",'\
            ' "app_hash": ""}, "data": {"txs": []}, "last_commit": {"blockID": '\
            ' {"hash": "", "parts": {"total": 0, "hash": ""}}, "precommits": []}}}}}}'

    event_queue = Queue()
    process_event(event_queue, event, 'test_stream_id')
    assert event_queue.empty()


def test_process_unknown_event():
    from bigchaindb.tendermint.event_stream import process_event

    event = '{"jsonrpc": "2.0", "id": "test_stream_id#event",'\
            ' "result": {"name": "UnknownEvent"}}'

    event_queue = Queue()
    process_event(event_queue, event, 'test_stream_id')
    assert event_queue.empty()


@pytest.mark.skip('This test will be an integration test.')
@pytest.mark.asyncio
async def test_subscribe_events(tendermint_ws_url):
    from bigchaindb.tendermint.event_stream import subscribe_events
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
    # TODO What else should be there? Right now, getting error.
