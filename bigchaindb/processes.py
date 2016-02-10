import logging
import multiprocessing as mp

import rethinkdb as r

from bigchaindb import Bigchain
from bigchaindb.voter import Voter
from bigchaindb.block import Block


logger = logging.getLogger(__name__)


class Processes(object):

    def __init__(self):
        # initialize the class
        self.q_new_block = mp.Queue()
        self.q_new_transaction = mp.Queue()

    def map_backlog(self):
        # listen to changes on the backlog and redirect the changes
        # to the correct queues

        # create a bigchain instance
        b = Bigchain()

        for change in r.table('backlog').changes().run(b.conn):

            # insert
            if change['old_val'] is None:
                self.q_new_transaction.put(change['new_val'])

            # delete
            if change['new_val'] is None:
                pass

            # update
            if change['new_val'] is not None and change['old_val'] is not None:
                pass

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
                pass

            # update
            elif change['new_val'] is not None and change['old_val'] is not None:
                pass

    def start(self):
        # instantiate block and voter
        block = Block(self.q_new_transaction)

        # initialize the processes
        p_map_bigchain = mp.Process(name='bigchain_mapper', target=self.map_bigchain)
        p_map_backlog = mp.Process(name='backlog_mapper', target=self.map_backlog)
        p_block = mp.Process(name='block', target=block.start)
        p_voter = Voter(self.q_new_block)

        # start the processes
        logger.info('starting bigchain mapper')
        p_map_bigchain.start()
        logger.info('starting backlog mapper')
        p_map_backlog.start()
        logger.info('starting block')
        p_block.start()

        logger.info('starting voter')
        p_voter.start()
