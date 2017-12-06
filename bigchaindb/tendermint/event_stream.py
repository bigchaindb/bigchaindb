import json
import logging
import time

import asyncio
import aiohttp

from bigchaindb.common.utils import gen_timestamp
from bigchaindb.events import EventTypes, Event
from bigchaindb.tendermint.utils import decode_txn_base64


HOST = 'localhost'
PORT = 46657
URL = f'ws://{HOST}:{PORT}/websocket'

PAYLOAD = {
    "method": "subscribe",
    "jsonrpc": "2.0",
    "params": ["NewBlock"],
    "id": "bigchaindb_stream"
}


logger = logging.getLogger(__name__)


async def connect_and_recv(event_queue):
    session = aiohttp.ClientSession()
    async with session.ws_connect(URL) as ws:
        logger.info('Connected to tendermint ws server')

        stream_id = "bigchaindb_stream_{}".format(gen_timestamp())
        await subscribe_events(ws, stream_id)

        async for msg in ws:
            process_event(event_queue, msg.data, stream_id)

            if msg.type in (aiohttp.WSMsgType.CLOSED,
                            aiohttp.WSMsgType.ERROR):
                session.close()
                raise aiohttp.ClientConnectionError()


def process_event(event_queue, event, stream_id):
    event_stream_id = stream_id + '#event'
    event = json.loads(event)

    if (event['id'] == event_stream_id and event['result']['name'] == 'NewBlock'):
        block = event['result']['data']['data']['block']
        block_id = block['header']['height']
        block_txs = block['data']['txs']

        # Only push non empty blocks
        if block_txs:
            block_txs = [json.loads(decode_txn_base64(txn)) for txn in block_txs]
            new_block = {'id': str(block_id), 'transactions': block_txs}
            event = Event(EventTypes.BLOCK_VALID, new_block)
            event_queue.put(event)


async def subscribe_events(ws, stream_id):
    PAYLOAD["id"] = stream_id
    await ws.send_str(json.dumps(PAYLOAD))


async def try_connect_and_recv(event_queue, gas):
    try:
        await connect_and_recv(event_queue)

    except Exception as e:
        logger.error('WebSocket connection failed with exception: {}'.format(e))
        if gas:
            time.sleep(2)
            await try_connect_and_recv(event_queue, gas-1)


def start(event_queue):
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(try_connect_and_recv(event_queue, 5))
    except (KeyboardInterrupt, SystemExit):
        logger.info('Shutting down tendermint event stream connection')
        return
