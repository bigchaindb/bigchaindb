from collections import Counter

from multipipes import Pipeline, Node

from bigchaindb.pipelines.utils import ChangeFeed
from bigchaindb import Bigchain


class Vote:

    def __init__(self):
        self.bigchain = Bigchain()
        last_voted = self.bigchain.get_last_voted_block()
        self.last_voted_id = last_voted['id']
        self.last_voted_number = last_voted['block_number']

        self.counters = Counter()
        self.validity = {}

    def ungroup(self, block):
        num_tx = len(block['block']['transactions'])
        for tx in block['block']['transactions']:
            yield tx, block['id'], num_tx

    def validate_tx(self, tx, block_id, num_tx):
        return bool(self.bigchain.is_valid_transaction(tx)), block_id, num_tx

    def vote(self, tx_validity, block_id, num_tx):
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
        self.bigchain.write_vote(vote)


def initial():
    b = Bigchain()
    initial = b.get_unvoted_blocks()
    return initial


def get_changefeed():
    return ChangeFeed('bigchain', 'insert', prefeed=initial())


def create_pipeline():
    voter = Vote()

    vote_pipeline = Pipeline([
        Node(voter.ungroup),
        Node(voter.validate_tx, fraction_of_cores=1),
        Node(voter.vote),
        Node(voter.write_vote)
    ])

    return vote_pipeline


def start():
    pipeline = create_pipeline()
    pipeline.setup(indata=get_changefeed())
    pipeline.start()
    return pipeline
