import logging
import multiprocessing as mp
import queue

import rethinkdb as r

import bigchaindb
from bigchaindb import Bigchain
from bigchaindb.monitor import Monitor
from bigchaindb.util import ProcessGroup


logger = logging.getLogger(__name__)


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
        self.initialized = mp.Event()
        self.monitor = Monitor()

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
            self.monitor.gauge('tx_queue_gauge',
                               self.q_tx_to_validate.qsize(),
                               rate=bigchaindb.config['statsd']['rate'])
            tx = self.q_tx_to_validate.get()

            # poison pill
            if tx == 'stop':
                self.q_tx_validated.put('stop')
                return

            with self.monitor.timer('validate_transaction', rate=bigchaindb.config['statsd']['rate']):
                is_valid_transaction = b.is_valid_transaction(tx)

            if is_valid_transaction:
                self.q_tx_validated.put(tx)
            else:
                self.q_tx_delete.put(tx['id'])

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
                self.q_tx_delete.put('stop')
                return

            with self.monitor.timer('write_block'):
                b.write_block(block)

            for tx in block['block']['transactions']:
                self.q_tx_delete.put(tx['id'])

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

        for i in range(mp.cpu_count()):
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

        # signal initialization complete
        self.initialized.set()

        self._start()
        logger.info('exiting block module...')

    def kill(self):
        for i in range(mp.cpu_count()):
            self.q_new_transaction.put('stop')

    def _start(self):
        """
        Initialize, spawn, and start the processes
        """

        # initialize the processes
        p_filter = ProcessGroup(name='filter_transactions', target=self.filter_by_assignee)
        p_validate = ProcessGroup(name='validate_transactions', target=self.validate_transactions)
        p_blocks = ProcessGroup(name='create_blocks', target=self.create_blocks)
        p_write = ProcessGroup(name='write_blocks', target=self.write_blocks)
        p_delete = ProcessGroup(name='delete_transactions', target=self.delete_transactions)

        # start the processes
        p_filter.start()
        p_validate.start()
        p_blocks.start()
        p_write.start()
        p_delete.start()


class BacklogDeleteRevert(Block):

    def __init__(self, q_backlog_delete):
        # invalid transactions can stay deleted
        self.q_tx_to_validate = q_backlog_delete
        self.q_tx_validated = mp.Queue()
        self.q_transaction_to_revert = mp.Queue()
        self.q_tx_delete = mp.Queue()

        self.monitor = Monitor()

    def locate_transactions(self):
        """
        Determine if a deleted transaction has made it into a block
        """
        # create bigchain instance
        b = Bigchain()

        while True:
            tx = self.q_tx_validated.get()

            # poison pill
            if tx == 'stop':
                self.q_tx_delete.put('stop')
                self.q_transaction_to_revert.put('stop')
                return

            # check if tx is in a (valid) block
            validity = b.get_blocks_status_containing_tx(tx['id'])

            if validity and list(validity.values()).count(Bigchain.BLOCK_VALID) == 1:
                # tx made it into a block, and can safely be deleted
                self.q_tx_delete.put(tx['id'])
            else:
                # valid tx not in any block, should be re-inserted into backlog
                self.q_transaction_to_revert.put(tx)

    def revert_deletes(self):
        """
        Put an incorrectly deleted transaction back in the backlog
        """
        # create bigchain instance
        b = Bigchain()

        while True:
            tx = self.q_transaction_to_revert.get()

            # poison pill
            if tx == 'stop':
                return

            b.write_transaction(tx)

    def empty_delete_q(self):
        """
        Empty the delete queue
        """

        while True:
            txid = self.q_tx_delete.get()

            # poison pill
            if txid == 'stop':
                return

    def kill(self):
        for i in range(mp.cpu_count()):
            self.q_tx_to_validate.put('stop')

    def start(self):
        """
        Initialize, spawn, and start the processes
        """

        # initialize the processes
        p_validate = ProcessGroup(name='validate_transactions', target=self.validate_transactions)
        p_locate = ProcessGroup(name='locate_transactions', target=self.locate_transactions)
        p_revert = ProcessGroup(name='revert_deletes', target=self.revert_deletes)
        p_empty_delete_q = ProcessGroup(name='empty_delete_q', target=self.empty_delete_q)

        # start the processes
        p_validate.start()
        p_locate.start()
        p_revert.start()
        p_empty_delete_q.start()
