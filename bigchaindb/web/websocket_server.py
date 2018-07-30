"""WebSocket server for the BigchainDB Event Stream API."""

# NOTE
#
# This module contains some functions and utilities that might belong to other
# modules. For now, I prefer to keep everything in this module. Why? Because
# those functions are needed only here.
#
# When we will extend this part of the project and we find that we need those
# functionalities elsewhere, we can start creating new modules and organizing
# things in a better way.


import json
import asyncio
import logging
import threading
from uuid import uuid4
from concurrent.futures import CancelledError

import aiohttp
from aiohttp import web

from bigchaindb import config
from bigchaindb.events import EventTypes


logger = logging.getLogger(__name__)
POISON_PILL = 'POISON_PILL'
EVENTS_ENDPOINT = '/api/v1/streams/valid_transactions'


def _multiprocessing_to_asyncio(in_queue, out_queue, loop):
    """Bridge between a synchronous multiprocessing queue
    and an asynchronous asyncio queue.

    Args:
        in_queue (multiprocessing.Queue): input queue
        out_queue (asyncio.Queue): output queue
    """

    while True:
        value = in_queue.get()
        loop.call_soon_threadsafe(out_queue.put_nowait, value)


class Dispatcher:
    """Dispatch events to websockets.

    This class implements a simple publish/subscribe pattern.
    """

    def __init__(self, event_source):
        """Create a new instance.

        Args:
            event_source: a source of events. Elements in the queue
            should be strings.
        """

        self.event_source = event_source
        self.subscribers = {}

    def subscribe(self, uuid, websocket):
        """Add a websocket to the list of subscribers.

        Args:
            uuid (str): a unique identifier for the websocket.
            websocket: the websocket to publish information.
        """

        self.subscribers[uuid] = websocket

    def unsubscribe(self, uuid):
        """Remove a websocket from the list of subscribers.

        Args:
            uuid (str): a unique identifier for the websocket.
        """

        del self.subscribers[uuid]

    @asyncio.coroutine
    def publish(self):
        """Publish new events to the subscribers."""

        while True:
            event = yield from self.event_source.get()
            str_buffer = []

            if event == POISON_PILL:
                return

            if isinstance(event, str):
                str_buffer.append(event)

            elif event.type == EventTypes.BLOCK_VALID:
                block = event.data

                for tx in block['transactions']:
                    asset_id = tx['id'] if tx['operation'] == 'CREATE' else tx['asset']['id']
                    data = {'height': block['height'],
                            'asset_id': asset_id,
                            'transaction_id': tx['id']}
                    str_buffer.append(json.dumps(data))

            for _, websocket in self.subscribers.items():
                for str_item in str_buffer:
                    yield from websocket.send_str(str_item)


@asyncio.coroutine
def websocket_handler(request):
    """Handle a new socket connection."""

    logger.debug('New websocket connection.')
    websocket = web.WebSocketResponse()
    yield from websocket.prepare(request)
    uuid = uuid4()
    request.app['dispatcher'].subscribe(uuid, websocket)

    while True:
        # Consume input buffer
        try:
            msg = yield from websocket.receive()
        except RuntimeError as e:
            logger.debug('Websocket exception: %s', str(e))
            break
        except CancelledError as e:
            logger.debug('Websocket closed')
            break
        if msg.type == aiohttp.WSMsgType.CLOSED:
            logger.debug('Websocket closed')
            break
        elif msg.type == aiohttp.WSMsgType.ERROR:
            logger.debug('Websocket exception: %s', websocket.exception())
            break

    request.app['dispatcher'].unsubscribe(uuid)
    return websocket


def init_app(event_source, *, loop=None):
    """Init the application server.

    Return:
        An aiohttp application.
    """

    dispatcher = Dispatcher(event_source)

    # Schedule the dispatcher
    loop.create_task(dispatcher.publish())

    app = web.Application(loop=loop)
    app['dispatcher'] = dispatcher
    app.router.add_get(EVENTS_ENDPOINT, websocket_handler)
    return app


def start(sync_event_source, loop=None):
    """Create and start the WebSocket server."""

    if not loop:
        loop = asyncio.get_event_loop()

    event_source = asyncio.Queue(loop=loop)

    bridge = threading.Thread(target=_multiprocessing_to_asyncio,
                              args=(sync_event_source, event_source, loop),
                              daemon=True)
    bridge.start()

    app = init_app(event_source, loop=loop)
    aiohttp.web.run_app(app,
                        host=config['wsserver']['host'],
                        port=config['wsserver']['port'])
