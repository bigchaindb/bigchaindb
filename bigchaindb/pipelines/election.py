import rethinkdb as r
from multipipes import Pipeline, Node

from bigchaindb.pipelines.utils import ChangeFeed
from bigchaindb import Bigchain


class Election:

    def __init__(self):
        self.bigchain = Bigchain()

    def check_for_quorum(self, next_vote):
        """
        Checks if block has enough invalid votes to make a decision
        """
        next_block = r.table('bigchain')\
            .get(next_vote['vote']['voting_for_block'])\
            .run(self.bigchain.conn)
        if self.bigchain.block_election_status(next_block) == self.bigchain.BLOCK_INVALID:
            return next_block

    def requeue_transactions(self, invalid_block):
        """
        Liquidates transactions from invalid blocks so they can be processed again
        """
        for tx in invalid_block['block']['transactions']:
            self.bigchain.write_transaction(tx)


def get_changefeed():
    return ChangeFeed(table='votes', operation='insert')


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