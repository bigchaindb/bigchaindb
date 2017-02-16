import pymongo
from bigchaindb.core import Bigchain
from collections import defaultdict
import logging as _logging
import time
import threading


log = _logging.getLogger('watchdog')


class Watchdog(threading.Thread):
    def __init__(self):
        self.b = Bigchain()
        self.sets = defaultdict(set)
        self.blocks = {}
        self.valid_blocks = set()
        self.utxos = set()
        self.txids = set()
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
        return self.error

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

        log.info('Watchdog listening')

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
                if type(e) == AssertionError:
                    e = e.args[0] if len(e.args) == 1 else e.args
                self.error = e
                log.warn('Watchdog caught: %s', repr(e))
                break

    def process(self, item):
        table = item['ns'].split('.')[1]
        getattr(self, 'process_' + table)(item)

    def process_bigchain(self, item):
        assert item['op'] == 'i', 'BIGCHAIN INSERT ONLY'
        block = item['o']
        log.info('Process block %s', block['id'])

        self.blocks[block['id']] = block
        self.sets['bigchain'].add(block['id'])

    def process_votes(self, item):
        block_id = item['o']['vote']['voting_for_block']
        log.info('Process vote for block: %s', block_id)

        block_id = item['o']['vote']['voting_for_block']
        assert item['op'] == 'i', 'VOTES INSERT ONLY'

        block = self.blocks[block_id]

        status = self.b.block_election_status(block_id,
                                              block['block']['voters'])

        if block_id in self.sets['valid-block']:
            pass  # ...
        elif status == 'valid':
            spends = list(get_block_spends(block))
            txids = [tx['id'] for tx in block['block']['transactions']]

            # Detect double spends
            assert len(spends) == len(set(spends)), \
                ('DOUBLE SPEND SINGLE BLOCK', block_id)
            assert set(spends).difference(self.utxos) == set(), \
                ('DOUBLE SPEND ACROSS BLOCKS', block_id)

            # Detect duplicate transactions
            assert len(txids) == len(set(txids)), \
                ('DUPLICATE TX SINGLE BLOCK', block_id)
            assert self.txids.intersection(txids) == set(), \
                ('DUPLICATE TX ACROSS BLOCKS', block_id)

            # All good
            self.valid_blocks.add(block_id)
            self.utxos.difference_update(spends)
            self.utxos.update(get_block_outputs(block))
            self.txids.update(txids)


def check_dupe_tx_in_block(block):
    return


def get_block_spends(block):
    for tx in block['block']['transactions']:
        if tx['operation'] == 'TRANSFER':
            for inp in tx['inputs']:
                ff = inp['fulfills']
                yield (ff['txid'], ff['output'])


def get_block_outputs(block):
    for tx in block['block']['transactions']:
        for i in range(len(tx['outputs'])):
            yield (tx['id'], i)
