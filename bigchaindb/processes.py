import logging
import multiprocessing as mp

import rethinkdb as r

import bigchaindb
from bigchaindb.pipelines import block
from bigchaindb import Bigchain
from bigchaindb.voter import Voter, Election
from bigchaindb.block import BlockDeleteRevert
from bigchaindb.web import server


logger = logging.getLogger(__name__)

BANNER = """
****************************************************************************
*                                                                          *
*   Initialization complete. BigchainDB is ready and waiting for events.   *
*   You can send events through the API documented at:                     *
*    - http://docs.bigchaindb.apiary.io/                                   *
*                                                                          *
*   Listening to client connections on: {:<15}                    *
*                                                                          *
****************************************************************************
"""


class Processes(object):

    def __init__(self):
        # initialize the class
        self.q_new_block = mp.Queue()
        self.q_block_new_vote = mp.Queue()
        self.q_revert_delete = mp.Queue()

    def map_bigchain(self):
        # listen to changes on the bigchain and redirect the changes
        # to the correct queues

        # create a bigchain instance
        b = Bigchain()

        for change in r.table('bigchain').changes().run(b.conn):

            # insert
            if change['old_val'] is None:
                self.q_new_block.put(change['new_val'])

            # delete
            elif change['new_val'] is None:
                # this should never happen in regular operation
                self.q_revert_delete.put(change['old_val'])

            # update (new vote)
            elif change['new_val'] is not None and change['old_val'] is not None:
                self.q_block_new_vote.put(change['new_val'])

    def start(self):
        logger.info('Initializing BigchainDB...')

        delete_reverter = BlockDeleteRevert(self.q_revert_delete)

        # start the web api
        app_server = server.create_server(bigchaindb.config['server'])
        p_webapi = mp.Process(name='webapi', target=app_server.run)
        p_webapi.start()

        # initialize the processes
        p_map_bigchain = mp.Process(name='bigchain_mapper', target=self.map_bigchain)
        p_block_delete_revert = mp.Process(name='block_delete_revert', target=delete_reverter.start)
        p_voter = Voter(self.q_new_block)
        p_election = Election(self.q_block_new_vote)
        # start the processes
        logger.info('starting bigchain mapper')
        p_map_bigchain.start()
        logger.info('starting backlog mapper')
        logger.info('starting block')
        block.start()
        p_block_delete_revert.start()

        logger.info('starting voter')
        p_voter.start()
        logger.info('starting election')
        p_election.start()

        # start message
        p_voter.initialized.wait()
        logger.info(BANNER.format(bigchaindb.config['server']['bind']))
