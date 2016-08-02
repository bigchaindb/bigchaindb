"""This module takes care of all the logic related to block voting.

The logic is encapsulated in the ``Vote`` class, while the sequence
of actions to do on transactions is specified in the ``create_pipeline``
function.
"""

from collections import Counter

from multipipes import Pipeline, Node

from bigchaindb.pipelines.utils import ChangeFeed
from bigchaindb import Bigchain


class Vote:
    """This class encapsulates the logic to vote on blocks.

    Note:
        Methods of this class will be executed in different processes.
    """

    def __init__(self):
        """Initialize the Block voter."""

        last_voted = Bigchain().get_last_voted_block()

        self.bigchain = Bigchain()
        self.last_voted_id = last_voted['id']

        self.counters = Counter()
        self.validity = {}

    def ungroup(self, block):
        """Given a block, ungroup the transactions in it.

        Args:
            block (dict): the block to process

        Returns:
            An iterator that yields a transaction, block id, and the total
            number of transactions contained in the block.
        """

        num_tx = len(block['block']['transactions'])
        for tx in block['block']['transactions']:
            yield tx, block['id'], num_tx

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
    initial = b.get_unvoted_blocks()
    return initial


def get_changefeed():
    """Create and return the changefeed for the bigchain table."""

    return ChangeFeed('bigchain', 'insert', prefeed=initial())


def create_pipeline():
    """Create and return the pipeline of operations to be distributed
    on different processes."""

    voter = Vote()

    vote_pipeline = Pipeline([
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
