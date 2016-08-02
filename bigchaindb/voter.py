import logging
import multiprocessing as mp

from bigchaindb import Bigchain


logger = logging.getLogger(__name__)


class Election(object):

    def __init__(self, q_block_new_vote):
        """
        Initialize the class with the needed queues.

        Initialize a queue where blocks with new votes will be held
        """
        self.q_block_new_vote = q_block_new_vote
        self.q_invalid_blocks = mp.Queue()

    def check_for_quorum(self):
        """
        Checks if block has enough invalid votes to make a decision
        """
        b = Bigchain()

        while True:
            next_block = self.q_block_new_vote.get()

            # poison pill
            if next_block == 'stop':
                self.q_invalid_blocks.put('stop')
                logger.info('clean exit')
                return

            if b.block_election_status(next_block) == 'invalid':
                self.q_invalid_blocks.put(next_block)

    def requeue_transactions(self):
        """
        Liquidates transactions from invalid blocks so they can be processed again
        """
        while True:
            invalid_block = self.q_invalid_blocks.get()

            # poison pill
            if invalid_block == 'stop':
                logger.info('clean exit')
                return

            b = Bigchain()
            for tx in invalid_block['block']['transactions']:
                b.write_transaction(tx)

    def kill(self):
        """
        Terminate processes
        """
        self.q_block_new_vote.put('stop')

    def start(self):
        """
        Initialize, spawn, and start the processes
        """

        # initialize the processes
        p_quorum_check = mp.Process(name='check_for_quorum', target=self.check_for_quorum)
        p_requeue_tx = mp.Process(name='requeue_tx', target=self.requeue_transactions)

        # start the processes
        p_quorum_check.start()
        p_requeue_tx.start()
