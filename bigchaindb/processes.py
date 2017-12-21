import logging
import multiprocessing as mp

import bigchaindb
from bigchaindb import config_utils
from bigchaindb.pipelines import vote, block, election, stale
from bigchaindb.events import Exchange, EventTypes
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


def start_events_plugins(exchange):
    plugins = config_utils.load_events_plugins(
        bigchaindb.config.get('events_plugins'))

    for name, plugin in plugins:
        logger.info('Loading events plugin %s', name)

        event_types = getattr(plugin, 'event_types', None)
        queue = exchange.get_subscriber_queue(event_types)

        mp.Process(name='events_plugin_{}'.format(name),
                   target=plugin.run,
                   args=(queue, )).start()


def start():
    logger.info('Initializing BigchainDB...')

    # Create a Exchange object.
    # The events queue needs to be initialized once and shared between
    # processes. This seems the best way to do it
    # At this point only the election processs and the event consumer require
    # this queue.
    exchange = Exchange()

    # start the processes
    logger.info('Starting block')
    block.start()

    logger.info('Starting voter')
    vote.start()

    logger.info('Starting stale transaction monitor')
    stale.start()

    logger.info('Starting election')
    election.start(events_queue=exchange.get_publisher_queue())

    # start the web api
    app_server = server.create_server(settings=bigchaindb.config['server'],
                                      log_config=bigchaindb.config['log'])
    p_webapi = mp.Process(name='webapi', target=app_server.run)
    p_webapi.start()

    logger.info('WebSocket server started')
    p_websocket_server = mp.Process(name='ws',
                                    target=websocket_server.start,
                                    args=(exchange.get_subscriber_queue(EventTypes.BLOCK_VALID),))
    p_websocket_server.start()

    # start message
    logger.info(BANNER.format(bigchaindb.config['server']['bind']))

    start_events_plugins(exchange)

    exchange.run()
