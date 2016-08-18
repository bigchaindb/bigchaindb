"""This module takes care of all the logic related to block creation.

The logic is encapsulated in the ``Block`` class, while the sequence
of actions to do on transactions is specified in the ``create_pipeline``
function.
"""

import logging

import rethinkdb as r
from multipipes import Pipeline, Node

from bigchaindb.pipelines.utils import ChangeFeed
from bigchaindb import Bigchain


logger = logging.getLogger(__name__)


class Block:
    """This class encapsulates the logic to create blocks.

    Note:
        Methods of this class will be executed in different processes.
    """

    def __init__(self):
        """Initialize the Block creator"""
        self.bigchain = Bigchain()
        self.txs = []

    def filter_tx(self, tx):
        """Filter a transaction.

        Args:
            tx (dict): the transaction to process.

        Returns:
            The transaction if assigned to the current node,
            ``None`` otherwise.
        """

        if tx['assignee'] == self.bigchain.me:
            tx.pop('assignee')
            return tx

    def delete_tx(self, tx):
        """Delete a transaction.

        Args:
            tx (dict): the transaction to delete.

        Returns:
            The transaction.
        """
        r.table('backlog')\
         .get(tx['id'])\
         .delete(durability='hard')\
         .run(self.bigchain.conn)

        return tx

    def validate_tx(self, tx):
        """Validate a transaction.

        Args:
            tx (dict): the transaction to validate.

        Returns:
            The transaction if valid, ``None`` otherwise.
        """
        tx = self.bigchain.is_valid_transaction(tx)
        if tx:
            return tx

    def create(self, tx, timeout=False):
        """Create a block.

        This method accumulates transactions to put in a block and outputs
        a block when one of the following conditions is true:
        - the size limit of the block has been reached, or
        - a timeout happened.

        Args:
            tx (dict): the transaction to validate, might be None if
                a timeout happens.
            timeout (bool): ``True`` if a timeout happened
                (Default: ``False``).

        Returns:
            The block, if a block is ready, or ``None``.
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
            block (dict): the block of transactions to write to the database.

        Returns:
            The block.
        """
        logger.info('Write new block %s with %s transactions',
                    block['id'],
                    len(block['block']['transactions']))
        self.bigchain.write_block(block)
        return block


def initial():
    """Return old transactions from the backlog."""

    b = Bigchain()

    rs = r.table('backlog')\
          .between([b.me, r.minval],
                   [b.me, r.maxval],
                   index='assignee__transaction_timestamp')\
          .order_by(index=r.asc('assignee__transaction_timestamp'))\
          .run(b.conn)
    return rs


def get_changefeed():
    """Create and return the changefeed for the backlog."""

    return ChangeFeed('backlog', ChangeFeed.INSERT, prefeed=initial())


def create_pipeline():
    """Create and return the pipeline of operations to be distributed
    on different processes."""

    block = Block()

    block_pipeline = Pipeline([
        Node(block.filter_tx),
        Node(block.delete_tx),
        Node(block.validate_tx, fraction_of_cores=1),
        Node(block.create, timeout=1),
        Node(block.write),
    ])

    return block_pipeline


def start():
    """Create, start, and return the block pipeline."""

    pipeline = create_pipeline()
    pipeline.setup(indata=get_changefeed())
    pipeline.start()
    return pipeline

