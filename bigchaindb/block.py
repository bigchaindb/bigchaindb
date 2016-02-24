import logging
import multiprocessing as mp
import queue

import rethinkdb as r

import bigchaindb
from bigchaindb import Bigchain
from bigchaindb.monitor import Monitor



logger = logging.getLogger(__name__)

monitor = Monitor()


class Block(object):

    def __init__(self, q_new_transaction):
        """
        Initialize the class with the needed
        """
        self._q_new_transaction = q_new_transaction
        self.q_new_transaction = None
        self.q_tx_to_validate = mp.Queue()
        self.q_tx_validated = mp.Queue()
        self.q_tx_delete = mp.Queue()
        self.q_block = mp.Queue()

    def filter_by_assignee(self):
        """
        Handle transactions that are assigned to me
        """

        # create a bigchain instance
        b = Bigchain()

        while True:
            tx = self.q_new_transaction.get()

            # poison pill
            if tx == 'stop':
                self.q_tx_to_validate.put('stop')
                return

            if tx['assignee'] == b.me:
                tx.pop('assignee')
                self.q_tx_to_validate.put(tx)

    def validate_transactions(self):
        """
        Checks if the incoming transactions are valid
        """

        # create a bigchain instance
        b = Bigchain()

        while True:
            monitor.gauge('tx_queue_gauge', self.q_tx_to_validate.qsize(), rate=bigchaindb.config['statsd']['rate'])
            tx = self.q_tx_to_validate.get()

            # poison pill
            if tx == 'stop':
                self.q_tx_delete.put('stop')
                self.q_tx_validated.put('stop')
                return

            self.q_tx_delete.put(tx['id'])
            if b.is_valid_transaction(tx):
                self.q_tx_validated.put(tx)

    def create_blocks(self):
        """
        Create a block with valid transactions
        """

        # create a bigchain instance
        b = Bigchain()
        stop = False

        while True:

            # read up to 1000 transactions
            validated_transactions = []
            for i in range(1000):
                try:
                    tx = self.q_tx_validated.get(timeout=5)
                except queue.Empty:
                    break

                # poison pill
                if tx == 'stop':
                    stop = True
                    break

                validated_transactions.append(tx)

            # if there are no transactions skip block creation
            if validated_transactions:
                # create block
                block = b.create_block(validated_transactions)
                self.q_block.put(block)

            if stop:
                self.q_block.put('stop')
                return

    def write_blocks(self):
        """
        Write blocks to the bigchain
        """

        # create bigchain instance
        b = Bigchain()

        # Write blocks
        while True:
            block = self.q_block.get()

            # poison pill
            if block == 'stop':
                return

            b.write_block(block)

    def delete_transactions(self):
        """
        Delete transactions from the backlog
        """
        # create bigchain instance
        b = Bigchain()
        stop = False

        while True:
            # try to delete in batch to reduce io
            tx_to_delete = []
            for i in range(1000):
                try:
                    tx = self.q_tx_delete.get(timeout=5)
                except queue.Empty:
                    break

                # poison pill
                if tx == 'stop':
                    stop = True
                    break

                tx_to_delete.append(tx)

            if tx_to_delete:
                r.table('backlog').get_all(*tx_to_delete).delete(durability='soft').run(b.conn)

            if stop:
                return

    def bootstrap(self):
        """
        Get transactions from the backlog that may have been assigned to this while it was
        online (not listening to the changefeed)
        """
        # create bigchain instance
        b = Bigchain()

        # create a queue to store initial results
        q_initial = mp.Queue()

        # get initial results
        initial_results = r.table('backlog')\
            .between([b.me, r.minval], [b.me, r.maxval], index='assignee__transaction_timestamp')\
            .order_by(index=r.asc('assignee__transaction_timestamp'))\
            .run(b.conn)

        # add results to the queue
        for result in initial_results:
            q_initial.put(result)
        q_initial.put('stop')

        return q_initial

    def start(self):
        """
        Bootstrap and start the processes
        """
        logger.info('bootstraping block module...')
        self.q_new_transaction = self.bootstrap()
        logger.info('finished reading past transactions')
        self._start()
        logger.info('finished bootstraping block module...')

        logger.info('starting block module...')
        self.q_new_transaction = self._q_new_transaction
        self._start()
        logger.info('exiting block module...')

    def _start(self):
        """
        Initialize, spawn, and start the processes
        """

        # initialize the processes
        p_filter = mp.Process(name='filter_transactions', target=self.filter_by_assignee)
        p_validate = mp.Process(name='validate_transactions', target=self.validate_transactions)
        p_blocks = mp.Process(name='create_blocks', target=self.create_blocks)
        p_write = mp.Process(name='write_blocks', target=self.write_blocks)
        p_delete = mp.Process(name='delete_transactions', target=self.delete_transactions)

        # start the processes
        p_filter.start()
        p_validate.start()
        p_blocks.start()
        p_write.start()
        p_delete.start()

        # join processes
        p_filter.join()
        p_validate.join()
        p_blocks.join()
        p_write.join()
        p_delete.join()
