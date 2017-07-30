import logging
import multiprocessing as mp

import bigchaindb
from bigchaindb.config_utils import load_block_publisher_plugins
from bigchaindb.pipelines import vote, block, election, stale
from bigchaindb.events import PubSub
from bigchaindb.web import server, websocket_server


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
    logger.info('Initializing BigchainDB...')

    # Create a PubSub object.
    # The events queue needs to be initialized once and shared between
    # processes. This seems the best way to do it
    # At this point only the election processs and the event consumer require
    # this queue.
    pubsub = PubSub()

    # start the processes
    logger.info('Starting block')
    block.start()

    logger.info('Starting voter')
    vote.start()

    logger.info('Starting stale transaction monitor')
    stale.start()

    logger.info('Starting election')
    election.start(events_queue=pubsub.get_publisher_queue())

    # start the web api
    app_server = server.create_server(bigchaindb.config['server'])
    p_webapi = mp.Process(name='webapi', target=app_server.run)
    p_webapi.start()

    logger.info('WebSocket server started')
    p_websocket_server = mp.Process(name='ws',
                                    target=websocket_server.start,
                                    args=(pubsub.get_subscriber_queue(),))
    p_websocket_server.start()

    # start message
    logger.info(BANNER.format(bigchaindb.config['server']['bind']))

    for name, plugin in load_block_publisher_plugins(bigchaindb.config.get('block_publishers', [])):
        logger.info('Loading block publisher plugin %s', name)
        mp.Process(name='block_publisher_{}'.format(name),
                   target=plugin.run,
                   args=(pubsub.get_subscriber_queue(),)).start()

    pubsub.run()
