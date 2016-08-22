"""This module takes care of all the logic related to block voting.

The logic is encapsulated in the ``Vote`` class, while the sequence
of actions to do on transactions is specified in the ``create_pipeline``
function.
"""

from collections import Counter

from multipipes import Pipeline, Node

from bigchaindb import config_utils, exceptions
from bigchaindb.pipelines.utils import ChangeFeed
from bigchaindb import Bigchain


def create_invalid_tx():
    """Create and return an invalid transaction.

    The transaction is invalid because it's missing the signature."""

    b = Bigchain()
    tx = b.create_transaction(b.me, b.me, None, 'CREATE')
    return tx


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
        last_voted = Bigchain().get_last_voted_block()
        self.consensus = config_utils.load_consensus_plugin()

        # This is the Bigchain instance that will be "shared" (aka: copied)
        # by all the subprocesses
        self.bigchain = Bigchain()
        self.last_voted_id = last_voted['id']

        self.counters = Counter()
        self.validity = {}

        self.invalid_dummy_tx = create_invalid_tx()

    def validate_block(self, block):
        if not self.bigchain.has_previous_vote(block):
            try:
                self.consensus.validate_block(self.bigchain, block)
                valid = True
            except (exceptions.InvalidHash,
                    exceptions.OperationError,
                    exceptions.InvalidSignature) as e:
                valid = False
            return block, valid

    def ungroup(self, block, valid):
        """Given a block, ungroup the transactions in it.

        Args:
            block (dict): the block to process

        Returns:
            ``None`` if the block has been already voted, an iterator that
            yields a transaction, block id, and the total number of
            transactions contained in the block otherwise.
        """

        # XXX: if a block is invalid we should skip the `validate_tx` step,
        # but since we are in a pipeline we cannot just jump to another
        # function. Hackish solution: generate an invalid transaction
        # and propagate it to the next steps of the pipeline
        if valid:
            num_tx = len(block['block']['transactions'])
            for tx in block['block']['transactions']:
                yield tx, block['id'], num_tx
        else:
            yield self.invalid_dummy_tx, block['id'], 1

    def validate_tx(self, tx, block_id, num_tx):
        """Validate a transaction.

        Args:
            tx (dict): the transaction to validate
            block_id (str): the id of block containing the transaction
            num_tx (int): the total number of transactions to process

        Returns:
            Three values are returned, the validity of the transaction,
            ``block_id``, ``num_tx``.
        """
        return bool(self.bigchain.is_valid_transaction(tx)), block_id, num_tx

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
        self.validity[block_id] = tx_validity and self.validity.get(block_id,
                                                                    True)

        if self.counters[block_id] == num_tx:
            vote = self.bigchain.vote(block_id,
                                      self.last_voted_id,
                                      self.validity[block_id])
            self.last_voted_id = block_id
            del self.counters[block_id]
            del self.validity[block_id]
            return vote

    def write_vote(self, vote):
        """Write vote to the database.

        Args:
            vote: the vote to write.
        """

        self.bigchain.write_vote(vote)
        return vote


def initial():
    """Return unvoted blocks."""
    b = Bigchain()
    rs = b.get_unvoted_blocks()
    return rs


def get_changefeed():
    """Create and return the changefeed for the bigchain table."""

    return ChangeFeed('bigchain', operation=ChangeFeed.INSERT, prefeed=initial())


def create_pipeline():
    """Create and return the pipeline of operations to be distributed
    on different processes."""

    voter = Vote()

    vote_pipeline = Pipeline([
        Node(voter.validate_block),
        Node(voter.ungroup),
        Node(voter.validate_tx, fraction_of_cores=1),
        Node(voter.vote),
        Node(voter.write_vote)
    ])

    return vote_pipeline


def start():
    """Create, start, and return the block pipeline."""

    pipeline = create_pipeline()
    pipeline.setup(indata=get_changefeed())
    pipeline.start()
    return pipeline
