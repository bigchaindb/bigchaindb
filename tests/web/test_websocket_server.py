import asyncio


@asyncio.coroutine
def test_websocket(test_client, loop):
    from bigchaindb.web.websocket_server import init_app, POISON_PILL

    event_source = asyncio.Queue(loop=loop)
    app = init_app(event_source, loop=loop)
    client = yield from test_client(app)
    ws = yield from client.ws_connect('/')
    yield from event_source.put('antani')
    yield from event_source.put(POISON_PILL)
    result = yield from ws.receive()
    assert result.data == 'antani'
