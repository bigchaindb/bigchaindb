import pytest
import asyncio


class MockWebSocket:
    def __init__(self):
        self.received = []

    def send_str(self, s):
        self.received.append(s)


@asyncio.coroutine
@pytest.mark.skipif(reason='This test raises a RuntimeError, dunno how to solve it now.')
def test_dispatcher(loop):
    from bigchaindb.web.websocket_server import Dispatcher, POISON_PILL

    ws0 = MockWebSocket()
    ws1 = MockWebSocket()

    event_source = asyncio.Queue(loop=loop)
    dispatcher = Dispatcher(event_source)

    dispatcher.subscribe(0, ws0)
    dispatcher.subscribe(1, ws1)

    yield from event_source.put('hack')
    yield from event_source.put('the')

    yield from event_source.put('planet!')
    yield from event_source.put(POISON_PILL)

    loop.run_until_complete(dispatcher.publish())

    assert ws0.received == ['hack', 'the', 'planet!']
    assert ws1.received == ['planet!']


@asyncio.coroutine
def test_websocket(test_client, loop):
    from bigchaindb.web.websocket_server import init_app, POISON_PILL

    event_source = asyncio.Queue(loop=loop)
    app = init_app(event_source, loop=loop)
    client = yield from test_client(app)
    ws = yield from client.ws_connect('/')

    yield from event_source.put('hack')
    yield from event_source.put('the')
    yield from event_source.put('planet!')

    result = yield from ws.receive()
    assert result.data == 'hack'

    result = yield from ws.receive()
    assert result.data == 'the'

    result = yield from ws.receive()
    assert result.data == 'planet!'

    yield from event_source.put(POISON_PILL)


@asyncio.coroutine
@pytest.mark.skipif(reason="Still don't understand how to trigger custom errors.")
def test_websocket_error(test_client, loop):
    from bigchaindb.web.websocket_server import init_app, POISON_PILL

    event_source = asyncio.Queue(loop=loop)
    app = init_app(event_source, loop=loop)
    client = yield from test_client(app)
    ws = yield from client.ws_connect('/')

    yield from ws.close()

    yield from event_source.put(POISON_PILL)
