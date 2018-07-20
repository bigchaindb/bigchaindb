import bigchaindb

import gevent
import logging

import setproctitle
import signal

from bigchaindb.tendermint.lib import BigchainDB
from bigchaindb.tendermint.core import App
from bigchaindb.web import server, websocket_server
from bigchaindb.tendermint import event_stream
from bigchaindb.events import Exchange, EventTypes
from bigchaindb.utils import Process


logger = logging.getLogger(__name__)

BANNER = """
****************************************************************************
*                                                                          *
*   ┏┓ ╻┏━╸┏━╸╻ ╻┏━┓╻┏┓╻╺┳┓┏┓    ┏━┓ ┏━┓ ╺┳┓┏━╸╻ ╻                         *
*   ┣┻┓┃┃╺┓┃  ┣━┫┣━┫┃┃┗┫ ┃┃┣┻┓   ┏━┛ ┃┃┃  ┃┃┣╸ ┃┏┛                         *
*   ┗━┛╹┗━┛┗━╸╹ ╹╹ ╹╹╹ ╹╺┻┛┗━┛   ┗━╸╹┗━┛╹╺┻┛┗━╸┗┛                          *
*   codename "fluffy cat"                                                  *
*   Initialization complete. BigchainDB Server is ready and waiting.       *
*                                                                          *
*   You can send HTTP requests via the HTTP API documented in the          *
*   BigchainDB Server docs at:                                             *
*    https://bigchaindb.com/http-api                                       *
*                                                                          *
*   Listening to client connections on: {:<15}                    *
*                                                                          *
****************************************************************************
"""


def sig_handler(server):
    logger.info('Shutting down BigchainDB. Goodbye!')
    server.stop()
    for p in bigchaindb.BIGCHAINDB_PROCESSES:
        p.terminate()


def start():
    # Exchange object for event stream api
    logger.info('Starting BigchainDB')
    exchange = Exchange()
    # start the web api
    app_server = server.create_server(
        settings=bigchaindb.config['server'],
        log_config=bigchaindb.config['log'],
        bigchaindb_factory=BigchainDB)
    p_webapi = Process(name='bigchaindb_webapi', target=app_server.run, daemon=True)
    bigchaindb.BIGCHAINDB_PROCESSES.append(p_webapi)
    p_webapi.start()

    # start message
    logger.info(BANNER.format(bigchaindb.config['server']['bind']))

    # start websocket server
    p_websocket_server = Process(name='bigchaindb_ws',
                                 target=websocket_server.start,
                                 daemon=True,
                                 args=(exchange.get_subscriber_queue(EventTypes.BLOCK_VALID),))
    bigchaindb.BIGCHAINDB_PROCESSES.append(p_websocket_server)
    p_websocket_server.start()

    # connect to tendermint event stream
    p_websocket_client = Process(name='bigchaindb_ws_to_tendermint',
                                 target=event_stream.start,
                                 daemon=True,
                                 args=(exchange.get_publisher_queue(),))
    bigchaindb.BIGCHAINDB_PROCESSES.append(p_websocket_client)
    p_websocket_client.start()

    p_exchange = Process(name='bigchaindb_exchange', target=exchange.run, daemon=True)
    bigchaindb.BIGCHAINDB_PROCESSES.append(p_exchange)
    p_exchange.start()

    # We need to import this after spawning the web server
    # because import ABCIServer will monkeypatch all sockets
    # for gevent.
    from abci import ABCIServer

    setproctitle.setproctitle('bigchaindb')

    # Start the ABCIServer and watch for signals to stop
    # the server and the relevant child bigchaindb.BIGCHAINDB_PROCESSES.
    app = ABCIServer(app=App())
    gevent.signal(signal.SIGTERM, sig_handler, app.server)
    gevent.signal(signal.SIGQUIT, sig_handler, app.server)
    gevent.signal(signal.SIGINT, sig_handler, app.server)

    app.server.serve_forever()

    for p in bigchaindb.BIGCHAINDB_PROCESSES:
        p.join()


if __name__ == '__main__':
    start()
