import pymongo
import logging as _logging

log = _logging.getLogger('watchdog')


class Watchdog:
    def __init__(self, bigchain):
        self.b = bigchain
        # A cache of blocks that are pending validation
        self.blocks = {}
        # Block validation results
        self.block_status = {}
        # Valid transaction outputs
        self.alltxos = set()
        # Valid unspent transaction outputs
        self.utxos = {}
        # Valid transaction IDs
        self.txids = set()

    def start(self):
        connection = self.b.connection
        self.start_ts = connection.run(
            connection.query().local.oplog.rs.find()
            .sort('$natural', pymongo.DESCENDING).limit(1)
            .next()['ts'])

        self.cursor = connection.run(
            connection.query().local.oplog.rs.find(
                {'ts': {'$gt': self.start_ts}},
                cursor_type=pymongo.CursorType.TAILABLE_AWAIT
            ))

    def join(self):
        while self.cursor.alive:
            try:
                self.record = self.cursor.next()
            except StopIteration:
                break

            try:
                self.process(self.record)
            except Exception as e:
                if type(e) == AssertionError:
                    return e.args[0] if len(e.args) == 1 else e.args
                raise

    def process(self, item):
        table = item['ns'].split('.')[1]
        getattr(self, 'process_' + table)(item)

    def process_backlog(self, _):
        pass

    def process_bigchain(self, item):
        assert item['op'] == 'i', 'BIGCHAIN INSERT ONLY'
        block = item['o']
        log.info('Process block %s', block['id'])

        self.blocks[block['id']] = block

    def process_votes(self, item):
        block_id = item['o']['vote']['voting_for_block']
        log.info('Process vote for block: %s', block_id)

        block_id = item['o']['vote']['voting_for_block']
        assert item['op'] == 'i', 'VOTES INSERT ONLY'

        block = self.blocks.get(block_id)
        assert block, ('VOTE NON EXISTENT BLOCK', block_id)

        status = self.b.block_election_status(block_id,
                                              block['block']['voters'])

        if block_id in self.block_status:
            assert status == self.block_status[block_id], \
                ('BLOCK ELECTION STATUS CHANGE', block_id)
            return

        if status == 'valid':
            self.process_valid_block(block)
            self.block_status[block_id] = 'valid'
        elif status == 'invalid':
            self.block_status[block_id] = 'invalid'

    def process_valid_block(self, block):
        txs = block['block']['transactions']
        txids = [tx['id'] for tx in txs]

        # Check for duplicate tx
        assert len(txids) == len(set(txids)), \
            ('DUPLICATE TX SINGLE BLOCK', block['id'])
        assert self.txids.intersection(txids) == set(), \
            ('DUPLICATE TX ACROSS BLOCKS', block['id'])
        self.txids.update(txids)

        # Check for double spend in block
        spends = list(get_block_spends(block))
        assert len(spends) == len(set(spends)), \
            ('DOUBLE SPEND SINGLE BLOCK', block['id'])

        # Spend each tx
        for tx in txs:
            if tx['operation'] == 'TRANSFER':
                self.spend(tx, block['id'])

        # Update TXOs
        for tx in txs:
            for i, output in enumerate(tx['outputs']):
                key = (tx['id'], i)
                self.utxos[key] = output
                self.alltxos.add(key)

    def spend(self, tx, block_id):
        # We'll assume that DOUBLE SPEND SINGLE BLOCK can catch any double
        # spend in a single TX
        balance = 0
        for inp in tx['inputs']:
            spend = spend_key(inp)
            assert spend in self.alltxos, ('INPUT DOES NOT EXIST', block_id)
            output = self.utxos.get(spend)
            assert output, ('DOUBLE SPEND ACROSS BLOCKS', block_id)
            balance -= output['amount']
            del self.utxos[spend]

        for i, output in enumerate(tx['outputs']):
            balance += output['amount']

        assert balance == 0, ('TX BALANCE ERROR', block_id)


def get_block_spends(block):
    for tx in block['block']['transactions']:
        if tx['operation'] == 'TRANSFER':
            for inp in tx['inputs']:
                yield spend_key(inp)


def spend_key(input_):
    return input_['fulfills']['txid'], input_['fulfills']['output']
