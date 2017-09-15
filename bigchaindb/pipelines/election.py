"""This module takes care of all the logic related to block status.

Specifically, what happens when a block becomes invalid.  The logic is
encapsulated in the ``Election`` class, while the sequence of actions
is specified in ``create_pipeline``.
"""
import logging

from multipipes import Pipeline, Node

import bigchaindb
from bigchaindb import backend
from bigchaindb.backend.changefeed import ChangeFeed
from bigchaindb.models import Block
from bigchaindb import Bigchain
from bigchaindb.events import EventTypes, Event


logger = logging.getLogger(__name__)
logger_results = logging.getLogger('pipeline.election.results')


class Election:
    """Election class."""

    def __init__(self, events_queue=None):
        self.bigchain = Bigchain()
        self.events_queue = events_queue

    def check_for_quorum(self, next_vote):
        """
        Checks if block has enough invalid votes to make a decision

        Args:
            next_vote: The next vote.

        """
        try:
            block_id = next_vote['vote']['voting_for_block']
            node = next_vote['node_pubkey']
        except KeyError:
            return

        next_block = self.bigchain.get_block(block_id)

        result = self.bigchain.block_election(next_block)
        self.handle_block_events(result, block_id)
        if result['status'] == self.bigchain.BLOCK_INVALID:
            return Block.from_dict(next_block)

        # Log the result
        if result['status'] != self.bigchain.BLOCK_UNDECIDED:
            msg = 'node:%s block:%s status:%s' % \
                (node, block_id, result['status'])
            # Extra data can be accessed via the log formatter.
            # See logging.dictConfig.
            logger_results.debug(msg, extra={
                'current_vote': next_vote,
                'election_result': result,
            })

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

    def handle_block_events(self, result, block_id):
        if self.events_queue:
            if result['status'] == self.bigchain.BLOCK_UNDECIDED:
                return
            elif result['status'] == self.bigchain.BLOCK_INVALID:
                event_type = EventTypes.BLOCK_INVALID
            elif result['status'] == self.bigchain.BLOCK_VALID:
                event_type = EventTypes.BLOCK_VALID

            event = Event(event_type, self.bigchain.get_block(block_id))
            self.events_queue.put(event)


def create_pipeline(events_queue=None):
    election = Election(events_queue=events_queue)

    election_pipeline = Pipeline([
        Node(election.check_for_quorum),
        Node(election.requeue_transactions)
    ])

    return election_pipeline


def get_changefeed():
    connection = backend.connect(**bigchaindb.config['database'])
    return backend.get_changefeed(connection, 'votes', ChangeFeed.INSERT)


def start(events_queue=None):
    pipeline = create_pipeline(events_queue=events_queue)
    pipeline.setup(indata=get_changefeed())
    pipeline.start()
    return pipeline
