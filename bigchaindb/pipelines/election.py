"""This module takes care of all the logic related to block status.

Specifically, what happens when a block becomes invalid.  The logic is
encapsulated in the ``Election`` class, while the sequence of actions
is specified in ``create_pipeline``.
"""
import logging

from multipipes import Pipeline, Node

from bigchaindb.pipelines.utils import ChangeFeed
from bigchaindb.models import Block
from bigchaindb import Bigchain


logger = logging.getLogger(__name__)


class Election:
    """Election class."""

    def __init__(self):
        self.bigchain = Bigchain()

    def check_for_quorum(self, next_vote):
        """
        Checks if block has enough invalid votes to make a decision

        Args:
            next_vote: The next vote.

        """
        next_block = self.bigchain.get_block(
            next_vote['vote']['voting_for_block'])

        block_status = self.bigchain.block_election_status(next_block['id'],
                                                           next_block['block']['voters'])
        if block_status == self.bigchain.BLOCK_INVALID:
            return Block.from_dict(next_block)

    def requeue_transactions(self, invalid_block):
        """
        Liquidates transactions from invalid blocks so they can be processed again
        """
        logger.info('Rewriting %s transactions from invalid block %s',
                    len(invalid_block.transactions),
                    invalid_block.id)
        for tx in invalid_block.transactions:
            self.bigchain.write_transaction(tx)
        return invalid_block


def get_changefeed():
    return ChangeFeed(table='votes', operation=ChangeFeed.INSERT)


def create_pipeline():
    election = Election()

    election_pipeline = Pipeline([
        Node(election.check_for_quorum),
        Node(election.requeue_transactions)
    ])

    return election_pipeline


def start():
    pipeline = create_pipeline()
    pipeline.setup(indata=get_changefeed())
    pipeline.start()
    return pipeline
