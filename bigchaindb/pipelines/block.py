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
from bigchaindb.common.exceptions import (SchemaValidationError, InvalidHash,
                                          InvalidSignature, AmountError)
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
        self.txs = []

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
        except (SchemaValidationError, InvalidHash, InvalidSignature,
                AmountError):
            return None

        if self.bigchain.transaction_exists(tx.id):
            # if the transaction already exists, we must check whether
            # it's in a valid or undecided block
            tx, status = self.bigchain.get_transaction(tx.id,
                                                       include_status=True)
            if status == self.bigchain.TX_VALID \
               or status == self.bigchain.TX_UNDECIDED:
                # if the tx is already in a valid or undecided block,
                # then it no longer should be in the backlog, or added
                # to a new block. We can delete and drop it.
                self.bigchain.delete_transaction(tx.id)
                return None

        tx_validated = self.bigchain.is_valid_transaction(tx)
        if tx_validated:
            return tx
        else:
            # if the transaction is not valid, remove it from the
            # backlog
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
        if tx:
            self.txs.append(tx)
        if len(self.txs) == 1000 or (timeout and self.txs):
            block = self.bigchain.create_block(self.txs)
            self.txs = []
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
