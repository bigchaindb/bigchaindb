from pytest import raises


class TestBlockModel(object):
    def test_block_initialization(self, monkeypatch):
        from bigchaindb.models import Block

        monkeypatch.setattr('time.time', lambda: 1)

        block = Block()
        assert block.transactions == []
        assert block.voters == []
        assert block.timestamp == '1'
        assert block.node_pubkey is None
        assert block.signature is None

        with raises(TypeError):
            Block('not a list or None')
        with raises(TypeError):
            Block(None, 'valid node_pubkey', 'valid timestamp',
                  'not a list or None')

    def test_block_serialization(self, b):
        from bigchaindb_common.crypto import hash_data
        from bigchaindb_common.transaction import Transaction
        from bigchaindb_common.util import gen_timestamp, serialize
        from bigchaindb.models import Block

        transactions = [Transaction.create([b.me], [b.me])]
        timestamp = gen_timestamp()
        voters = ['Qaaa', 'Qbbb']
        expected_block = {
            'timestamp': timestamp,
            'transactions': [tx.to_dict() for tx in transactions],
            'node_pubkey': b.me,
            'voters': voters,
        }
        expected = {
            'id': hash_data(serialize(expected_block)),
            'block': expected_block,
            'signature': None,
        }

        block = Block(transactions, b.me, timestamp, voters)

        assert block.to_dict() == expected

    def test_block_invalid_serializaton(self):
        from bigchaindb_common.exceptions import OperationError
        from bigchaindb.models import Block

        block = Block([])
        with raises(OperationError):
            block.to_dict()

    def test_block_deserialization(self, b):
        from bigchaindb_common.crypto import hash_data
        from bigchaindb_common.transaction import Transaction
        from bigchaindb_common.util import gen_timestamp, serialize
        from bigchaindb.models import Block

        transactions = [Transaction.create([b.me], [b.me])]
        timestamp = gen_timestamp()
        voters = ['Qaaa', 'Qbbb']
        expected = Block(transactions, b.me, timestamp, voters)

        block = {
            'timestamp': timestamp,
            'transactions': [tx.to_dict() for tx in transactions],
            'node_pubkey': b.me,
            'voters': voters,
        }

        block_body = {
            'id': hash_data(serialize(block)),
            'block': block,
            'signature': None,
        }

        assert expected == Block.from_dict(block_body)

    def test_block_invalid_id_deserialization(self, b):
        from bigchaindb_common.exceptions import InvalidHash
        from bigchaindb.models import Block

        block = {
            'id': 'an invalid id',
            'block': {
                'node_pubkey': b.me,
            }
        }

        with raises(InvalidHash):
            Block.from_dict(block)

    def test_block_invalid_signature_deserialization(self, b):
        from bigchaindb_common.crypto import hash_data
        from bigchaindb_common.exceptions import InvalidSignature
        from bigchaindb_common.transaction import Transaction
        from bigchaindb_common.util import gen_timestamp, serialize
        from bigchaindb.models import Block

        transactions = [Transaction.create([b.me], [b.me])]
        timestamp = gen_timestamp()
        voters = ['Qaaa', 'Qbbb']

        block = {
            'timestamp': timestamp,
            'transactions': [tx.to_dict() for tx in transactions],
            'node_pubkey': b.me,
            'voters': voters,
        }

        block_body = {
            'id': hash_data(serialize(block)),
            'block': block,
            'signature': 'an invalid signature',
        }

        with raises(InvalidSignature):
            Block.from_dict(block_body)

    def test_compare_blocks(self, b):
        from bigchaindb_common.transaction import Transaction
        from bigchaindb.models import Block

        transactions = [Transaction.create([b.me], [b.me])]

        assert Block() != 'invalid comparison'
        assert Block(transactions) == Block(transactions)

    def test_sign_block(self, b):
        from bigchaindb_common.crypto import SigningKey, VerifyingKey
        from bigchaindb_common.transaction import Transaction
        from bigchaindb_common.util import gen_timestamp, serialize
        from bigchaindb.models import Block

        transactions = [Transaction.create([b.me], [b.me])]
        timestamp = gen_timestamp()
        voters = ['Qaaa', 'Qbbb']
        expected_block = {
            'timestamp': timestamp,
            'transactions': [tx.to_dict() for tx in transactions],
            'node_pubkey': b.me,
            'voters': voters,
        }
        expected_block_serialized = serialize(expected_block)
        expected = SigningKey(b.me_private).sign(expected_block_serialized)
        block = Block(transactions, b.me, timestamp, voters)
        block = block.sign(b.me_private)
        assert block.signature == expected

        verifying_key = VerifyingKey(b.me)
        assert verifying_key.verify(expected_block_serialized, block.signature)
