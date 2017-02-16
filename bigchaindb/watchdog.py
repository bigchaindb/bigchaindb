import pymongo
from bigchaindb.core import Bigchain
from collections import defaultdict
import time
import threading


class Watchdog(threading.Thread):
    def __init__(self):
        self.b = Bigchain()
        self.sets = defaultdict(set)
        self.blocks = {}
        self.error = None
        self.ready = False
        self.stop = False
        super(Watchdog, self).__init__()

    def start(self):
        super(Watchdog, self).start()
        while not self.ready:
            time.sleep(0.001)

    def join(self):
        self.stop = True
        super(Watchdog, self).join()
        if self.error:
            raise self.error

    def run(self):
        connection = self.b.connection

        last_ts = connection.run(
            connection.query().local.oplog.rs.find()
            .sort('$natural', pymongo.DESCENDING).limit(1)
            .next()['ts'])

        cursor = connection.run(
            connection.query().local.oplog.rs.find(
                {'ts': {'$gt': last_ts}},
                cursor_type=pymongo.CursorType.TAILABLE_AWAIT
            ))

        self.ready = True

        while cursor.alive:
            try:
                self.record = cursor.next()
            except StopIteration:
                if self.stop:
                    break
                continue

            try:
                self.process(self.record)
            except Exception as e:
                self.error = e
                raise

    def process(self, item):
        table = item['ns'].split('.')[1]
        getattr(self, 'process_' + table)(item)

    def process_bigchain(self, item):
        assert item['op'] == 'i', 'BIGCHAIN INSERT ONLY'
        block = item['o']

        self.blocks[block['id']] = block
        self.sets['bigchain'].add(block['id'])

        self.check_dupe_tx_in_block(block)
        self.check_double_spend_in_block(block)

    def process_votes(self, item):
        assert item['op'] == 'i', 'VOTES INSERT ONLY'
        block_id = item['o']['vote']['voting_for_block']

        block = self.blocks[block_id]

        # assert no double vote
        # assert no status change (valid -> invalid)

        status = self.b.block_election_status(block_id,
                                              block['block']['voters'])
        if status == 'valid':
            self.sets['valid-blocks'].add(block_id)
            # TODO: intersections must be null
            # TODO: dont use self.sets
            self.sets['valid-tx'].update(self.sets['block-txs-' + block_id])
            self.sets['txo'].update(self.sets['block-spends-' + block_id])

    def check_double_spend_in_block(self, block):
        # TODO: This should warn but not error, since it's not part of
        # valid set
        spends = set()
        for tx in block['block']['transactions']:
            if tx['operation'] == 'TRANSFER':
                for inp in tx['inputs']:
                    ff = inp['fulfills']
                    ff = (ff['txid'], ff['output'])
                    assert ff not in spends, 'DOUBLE SPEND IN BLOCK'
                    spends.add(ff)

    def check_dupe_tx_in_block(self, block):
        txids = [tx['id'] for tx in block['block']['transactions']]
        assert len(txids) == len(set(txids)), 'BLOCK DUPLICATE TX'
        self.sets['block-txs-' + block['id']].update(txids)
