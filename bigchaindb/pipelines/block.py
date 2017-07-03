"""This module takes care of all the logic related to block creation.

The logic is encapsulated in the ``BlockPipeline`` class, while the sequence
of actions to do on transactions is specified in the ``create_pipeline``
function.
"""

import logging

from multipipes import Pipeline, Node, Pipe

import bigchaindb
from bigchaindb import backend
from bigchaindb.backend.changefeed import ChangeFeed
from bigchaindb.models import Transaction
from bigchaindb.common.exceptions import (ValidationError,
                                          GenesisBlockAlreadyExistsError)
from bigchaindb import Bigchain


logger = logging.getLogger(__name__)


class BlockPipeline:
    """This class encapsulates the logic to create blocks.

    Note:
        Methods of this class will be executed in different processes.
    """

    def __init__(self):
        """Initialize the BlockPipeline creator"""
        self.bigchain = Bigchain()
        self.txs = tx_collector()

    def filter_tx(self, tx):
        """Filter a transaction.

        Args:
            tx (dict): the transaction to process.

        Returns:
            dict: The transaction if assigned to the current node,
            ``None`` otherwise.
        """
        if tx['assignee'] == self.bigchain.me:
            tx.pop('assignee')
            tx.pop('assignment_timestamp')
            return tx

    def validate_tx(self, tx):
        """Validate a transaction.

        Also checks if the transaction already exists in the blockchain. If it
        does, or it's invalid, it's deleted from the backlog immediately.

        Args:
            tx (dict): the transaction to validate.

        Returns:
            :class:`~bigchaindb.models.Transaction`: The transaction if valid,
            ``None`` otherwise.
        """
        try:
            tx = Transaction.from_dict(tx)
        except ValidationError:
            return None

        # If transaction is in any VALID or UNDECIDED block we
        # should not include it again
        if not self.bigchain.is_new_transaction(tx.id):
            self.bigchain.delete_transaction(tx.id)
            return None

        # If transaction is not valid it should not be included
        try:
            # Do not allow an externally submitted GENESIS transaction.
            # A simple check is enough as a pipeline is started only after the
            # creation of GENESIS block, or after the verification of a GENESIS
            # block. Voting will fail at a later stage if the GENESIS block is
            # absent.
            if tx.operation == Transaction.GENESIS:
                raise GenesisBlockAlreadyExistsError('Duplicate GENESIS transaction')

            tx.validate(self.bigchain)
            return tx
        except ValidationError as e:
            logger.warning('Invalid tx: %s', e)
            self.bigchain.delete_transaction(tx.id)
            return None

    def create(self, tx, timeout=False):
        """Create a block.

        This method accumulates transactions to put in a block and outputs
        a block when one of the following conditions is true:
        - the size limit of the block has been reached, or
        - a timeout happened.

        Args:
            tx (:class:`~bigchaindb.models.Transaction`): the transaction
                to validate, might be None if a timeout happens.
            timeout (bool): ``True`` if a timeout happened
                (Default: ``False``).

        Returns:
            :class:`~bigchaindb.models.Block`: The block,
            if a block is ready, or ``None``.
        """
        txs = self.txs.send(tx)
        if len(txs) == 1000 or (timeout and txs):
            block = self.bigchain.create_block(txs)
            self.txs = tx_collector()
            return block

    def write(self, block):
        """Write the block to the Database.

        Args:
            block (:class:`~bigchaindb.models.Block`): the block of
                transactions to write to the database.

        Returns:
            :class:`~bigchaindb.models.Block`: The Block.
        """
        logger.info('Write new block %s with %s transactions',
                    block.id, len(block.transactions))
        self.bigchain.write_block(block)
        self.bigchain.statsd.incr('pipelines.block.throughput',
                                  len(block.transactions))
        return block

    def delete_tx(self, block):
        """Delete transactions.

        Args:
            block (:class:`~bigchaindb.models.Block`): the block
                containg the transactions to delete.

        Returns:
            :class:`~bigchaindb.models.Block`: The block.
        """
        self.bigchain.delete_transaction(*[tx.id for tx in block.transactions])
        return block


def tx_collector():
    """ A helper to deduplicate transactions """

    def snowflake():
        txids = set()
        txs = []
        while True:
            tx = yield txs
            if tx:
                if tx.id not in txids:
                    txids.add(tx.id)
                    txs.append(tx)
                else:
                    logger.info('Refusing to add tx to block twice: ' +
                                tx.id)

    s = snowflake()
    s.send(None)
    return s


def create_pipeline():
    """Create and return the pipeline of operations to be distributed
    on different processes."""

    block_pipeline = BlockPipeline()

    pipeline = Pipeline([
        Pipe(maxsize=1000),
        Node(block_pipeline.filter_tx),
        Node(block_pipeline.validate_tx, fraction_of_cores=1),
        Node(block_pipeline.create, timeout=1),
        Node(block_pipeline.write),
        Node(block_pipeline.delete_tx),
    ])

    return pipeline


def get_changefeed():
    connection = backend.connect(**bigchaindb.config['database'])
    return backend.get_changefeed(connection, 'backlog',
                                  ChangeFeed.INSERT | ChangeFeed.UPDATE)


def start():
    """Create, start, and return the block pipeline."""
    pipeline = create_pipeline()
    pipeline.setup(indata=get_changefeed())
    pipeline.start()
    return pipeline
