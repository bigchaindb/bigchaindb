"""WebSocket server for the BigchainDB Event Stream API."""

import asyncio
import logging
from uuid import uuid4

import aiohttp
from aiohttp import web


logger = logging.getLogger(__name__)
POISON_PILL = 'POISON_PILL'


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

    def subscribe(self, uuid, ws):
        """Add a websocket to the list of subscribers.

        Args:
            uuid (str): a unique identifier for the websocket.
            ws: the websocket to publish information.
        """

        self.subscribers[uuid] = ws

    @asyncio.coroutine
    def publish(self):
        """Publish new events to the subscribers."""

        while True:
            event = yield from self.event_source.get()
            if event == POISON_PILL:
                return
            for uuid, ws in self.subscribers.items():
                ws.send_str(event)


@asyncio.coroutine
def websocket_handler(request):
    """Handle a new socket connection."""

    logger.debug('New websocket connection.')
    ws = web.WebSocketResponse()
    yield from ws.prepare(request)
    uuid = uuid4()
    request.app['dispatcher'].subscribe(uuid, ws)

    while True:
        # Consume input buffer
        msg = yield from ws.receive()
        if msg.type == aiohttp.WSMsgType.ERROR:
            logger.debug('Websocket exception: {}'.format(ws.exception()))
            return


def init_app(event_source, loop=None):
    """Init the application server.

    Return:
        An aiohttp application.
    """

    dispatcher = Dispatcher(event_source)

    # Schedule the dispatcher
    loop.create_task(dispatcher.publish())

    app = web.Application(loop=loop)
    app['dispatcher'] = dispatcher
    app.router.add_get('/', websocket_handler)
    return app


@asyncio.coroutine
def constant_event_source(event_source):
    while True:
        yield from asyncio.sleep(1)
        yield from event_source.put('meow')


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    event_source = asyncio.Queue()

    loop.create_task(constant_event_source(event_source))
    app = init_app(event_source, loop=loop)
    aiohttp.web.run_app(app, port=9985)
