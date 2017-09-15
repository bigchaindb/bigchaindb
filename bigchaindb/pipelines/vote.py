"""This module takes care of all the logic related to block voting.

The logic is encapsulated in the ``Vote`` class, while the sequence
of actions to do on transactions is specified in the ``create_pipeline``
function.
"""

import logging
from collections import Counter

from multipipes import Pipeline, Node

from bigchaindb import backend, Bigchain
from bigchaindb.models import Transaction, Block, FastTransaction
from bigchaindb.common import exceptions


logger = logging.getLogger(__name__)


class Vote:
    """This class encapsulates the logic to vote on blocks.

    Note:
        Methods of this class will be executed in different processes.
    """

    def __init__(self):
        """Initialize the Block voter."""

        # Since cannot share a connection to RethinkDB using multiprocessing,
        # we need to create a temporary instance of BigchainDB that we use
        # only to query RethinkDB

        # This is the Bigchain instance that will be "shared" (aka: copied)
        # by all the subprocesses

        self.bigchain = Bigchain()
        self.last_voted_id = Bigchain().get_last_voted_block().id

        self.counters = Counter()
        self.blocks_validity_status = {}

        dummy_tx = Transaction.create([self.bigchain.me],
                                      [([self.bigchain.me], 1)]).to_dict()
        self.invalid_dummy_tx = dummy_tx

    def validate_block(self, block_dict):
        if not self.bigchain.has_previous_vote(block_dict['id']):
            try:
                block = Block.from_db(self.bigchain, block_dict, from_dict_kwargs={
                    'tx_construct': FastTransaction
                })
            except (exceptions.InvalidHash):
                # XXX: if a block is invalid we should skip the `validate_tx`
                # step, but since we are in a pipeline we cannot just jump to
                # another function. Hackish solution: generate an invalid
                # transaction and propagate it to the next steps of the
                # pipeline.
                return block_dict['id'], [self.invalid_dummy_tx]
            try:
                block._validate_block(self.bigchain)
            except exceptions.ValidationError:
                # XXX: if a block is invalid we should skip the `validate_tx`
                # step, but since we are in a pipeline we cannot just jump to
                # another function. Hackish solution: generate an invalid
                # transaction and propagate it to the next steps of the
                # pipeline.
                return block.id, [self.invalid_dummy_tx]
            return block.id, block_dict['block']['transactions']

    def ungroup(self, block_id, transactions):
        """Given a block, ungroup the transactions in it.

        Args:
            block_id (str): the id of the block in progress.
            transactions (list(dict)): transactions of the block in
                progress.

        Returns:
            ``None`` if the block has been already voted, an iterator that
            yields a transaction, block id, and the total number of
            transactions contained in the block otherwise.
        """

        num_tx = len(transactions)
        for tx in transactions:
            yield tx, block_id, num_tx

    def validate_tx(self, tx_dict, block_id, num_tx):
        """Validate a transaction. Transaction must also not be in any VALID
           block.

        Args:
            tx_dict (dict): the transaction to validate
            block_id (str): the id of block containing the transaction
            num_tx (int): the total number of transactions to process

        Returns:
            Three values are returned, the validity of the transaction,
            ``block_id``, ``num_tx``.
        """

        try:
            tx = Transaction.from_dict(tx_dict)
            new = self.bigchain.is_new_transaction(tx.id, exclude_block_id=block_id)
            if not new:
                raise exceptions.ValidationError('Tx already exists, %s', tx.id)
            tx.validate(self.bigchain)
            valid = True
        except exceptions.ValidationError as e:
            valid = False
            logger.warning('Invalid tx: %s', e)

        return valid, block_id, num_tx

    def vote(self, tx_validity, block_id, num_tx):
        """Collect the validity of transactions and cast a vote when ready.

        Args:
            tx_validity (bool): the validity of the transaction
            block_id (str): the id of block containing the transaction
            num_tx (int): the total number of transactions to process

        Returns:
            None, or a vote if a decision has been reached.
        """

        self.counters[block_id] += 1
        self.blocks_validity_status[block_id] = tx_validity and self.blocks_validity_status.get(block_id,
                                                                                                True)

        if self.counters[block_id] == num_tx:
            vote = self.bigchain.vote(block_id,
                                      self.last_voted_id,
                                      self.blocks_validity_status[block_id])
            self.last_voted_id = block_id
            del self.counters[block_id]
            del self.blocks_validity_status[block_id]
            return vote, num_tx

    def write_vote(self, vote, num_tx):
        """Write vote to the database.

        Args:
            vote: the vote to write.
        """
        validity = 'valid' if vote['vote']['is_block_valid'] else 'invalid'
        logger.info("Voting '%s' for block %s", validity,
                    vote['vote']['voting_for_block'])
        self.bigchain.write_vote(vote)
        self.bigchain.statsd.incr('pipelines.vote.throughput', num_tx)
        return vote


def create_pipeline():
    """Create and return the pipeline of operations to be distributed
    on different processes."""

    voter = Vote()

    return Pipeline([
        Node(voter.validate_block),
        Node(voter.ungroup),
        Node(voter.validate_tx, fraction_of_cores=1),
        Node(voter.vote),
        Node(voter.write_vote)
    ])


def get_changefeed():
    """Create and return ordered changefeed of blocks starting from
       last voted block"""
    b = Bigchain()
    last_block_id = b.get_last_voted_block().id
    feed = backend.query.get_new_blocks_feed(b.connection, last_block_id)
    return Node(feed.__next__, name='changefeed')


def start():
    """Create, start, and return the block pipeline."""

    pipeline = create_pipeline()
    pipeline.setup(indata=get_changefeed())
    pipeline.start()
    return pipeline
