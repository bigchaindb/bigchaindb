"""WebSocket server for the BigchainDB Event Stream API."""

import asyncio
from uuid import uuid4

from aiohttp import web


class PoisonPill:
    pass


POISON_PILL = PoisonPill()


class Dispatcher:

    def __init__(self, event_source):
        self.event_source = event_source
        self.subscribers = {}

    def subscribe(self, uuid, ws):
        self.subscribers[uuid] = ws

    @asyncio.coroutine
    def publish(self):
        while True:
            event = yield from self.event_source.get()
            if event == POISON_PILL:
                return
            for uuid, ws in self.subscribers.items():
                ws.send_str(event)


@asyncio.coroutine
def websocket_handler(request):
    ws = web.WebSocketResponse()
    yield from ws.prepare(request)
    uuid = uuid4()
    request.app['dispatcher'].subscribe(uuid, ws)
    while True:
        # Consume input buffer
        yield from ws.receive()
    return ws


def init_app(event_source, loop=None):
    dispatcher = Dispatcher(event_source)

    # Schedule the dispatcher
    loop.create_task(dispatcher.publish())

    app = web.Application(loop=loop)
    app['dispatcher'] = dispatcher
    app.router.add_get('/', websocket_handler)
    return app
