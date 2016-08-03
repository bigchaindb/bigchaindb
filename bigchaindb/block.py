import logging
import multiprocessing as mp
import queue

import rethinkdb as r

import bigchaindb
from bigchaindb import Bigchain
from bigchaindb.monitor import Monitor
from bigchaindb.util import ProcessGroup


logger = logging.getLogger(__name__)


class BlockDeleteRevert(object):

    def __init__(self, q_delete_to_revert):
        self.q_delete_to_revert = q_delete_to_revert

    def write_blocks(self):
        """
        Write blocks to the bigchain
        """

        # create bigchain instance
        b = Bigchain()

        # Write blocks
        while True:
            block = self.q_delete_to_revert.get()

            # poison pill
            if block == 'stop':
                return

            b.write_block(block)

    def kill(self):
        for i in range(mp.cpu_count()):
            self.q_delete_to_revert.put('stop')

    def start(self):
        """
        Initialize, spawn, and start the processes
        """

        # initialize the processes
        p_write = ProcessGroup(name='write_blocks', target=self.write_blocks)

        # start the processes
        p_write.start()
