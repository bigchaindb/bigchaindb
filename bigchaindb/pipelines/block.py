import rethinkdb as r
from pipes import Pipeline, Node

from bigchaindb.pipelines.utils import ChangeFeed
from bigchaindb import Bigchain


class Block:

    def __init__(self):
        self.bigchain = Bigchain()
        self.txs = []

    def filter_tx(self, tx):
        if tx['assignee'] == self.bigchain.me:
            tx.pop('assignee')
            return tx

    def delete_tx(self, tx):
        r.table('backlog')\
         .get(tx['id'])\
         .delete(durability='hard')\
         .run(self.bigchain.conn)

        return tx

    def validate_tx(self, tx):
        tx = self.bigchain.is_valid_transaction(tx)
        if tx:
            return tx

    def create(self, tx, timeout=False):
        if tx:
            self.txs.append(tx)
        if self.txs and (len(self.txs) == 1000 or timeout):
            block = self.bigchain.create_block(self.txs)
            self.txs = []
            return block

    def write(self, block):
        self.bigchain.write_block(block)
        return block


def initial():
    b = Bigchain()

    rs = r.table('backlog')\
          .between([b.me, r.minval],
                   [b.me, r.maxval],
                   index='assignee__transaction_timestamp')\
          .order_by(index=r.asc('assignee__transaction_timestamp'))\
          .run(b.conn)
    return rs


def get_changefeed():
    return ChangeFeed('backlog', 'insert', prefeed=initial())


def create_pipeline():
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
    pipeline = create_pipeline()
    pipeline.setup(indata=get_changefeed())
    pipeline.start()
    return pipeline


if __name__ == '__main__':
    start()
