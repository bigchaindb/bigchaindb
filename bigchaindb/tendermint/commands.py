import logging
import subprocess
import multiprocessing as mp

import bigchaindb
from bigchaindb.tendermint.lib import BigchainDB
from bigchaindb.tendermint.core import App
from bigchaindb.web import server


logger = logging.getLogger(__name__)

BANNER = """
****************************************************************************
*                                                                          *
*   Initialization complete. BigchainDB Server is ready and waiting.       *
*   You can send HTTP requests via the HTTP API documented in the          *
*   BigchainDB Server docs at:                                             *
*    https://bigchaindb.com/http-api                                       *
*                                                                          *
*   Listening to client connections on: {:<15}                    *
*                                                                          *
****************************************************************************
"""


def start():
    # start the web api
    app_server = server.create_server(
        settings=bigchaindb.config['server'],
        log_config=bigchaindb.config['log'],
        bigchaindb_factory=BigchainDB)
    p_webapi = mp.Process(name='webapi', target=app_server.run)
    p_webapi.start()

    # start message
    print(BANNER.format(bigchaindb.config['server']['bind']))

    subprocess.Popen(['tendermint', 'node', '--consensus.create_empty_blocks=false'])

    # We need to import this after spawning the web server
    # because import ABCIServer will monkeypatch all sockets
    # for gevent.
    from abci import ABCIServer

    app = ABCIServer(app=App())
    app.run()


if __name__ == '__main__':
    start()
