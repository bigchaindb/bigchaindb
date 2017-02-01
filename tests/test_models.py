from pytest import raises


class TestTransactionModel(object):
    def test_validating_an_invalid_transaction(self, b):
        from bigchaindb.models import Transaction

        tx = Transaction.create([b.me], [([b.me], 1)])
        tx.operation = 'something invalid'

        with raises(TypeError):
            tx.validate(b)

        tx.operation = 'CREATE'
        tx.inputs = []
        with raises(ValueError):
            tx.validate(b)


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
        from bigchaindb.common.crypto import hash_data
        from bigchaindb.common.utils import gen_timestamp, serialize
        from bigchaindb.models import Block, Transaction

        transactions = [Transaction.create([b.me], [([b.me], 1)])]
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
        from bigchaindb.common.exceptions import OperationError
        from bigchaindb.models import Block

        block = Block([])
        with raises(OperationError):
            block.to_dict()

    def test_block_deserialization(self, b):
        from bigchaindb.common.crypto import hash_data
        from bigchaindb.common.utils import gen_timestamp, serialize
        from bigchaindb.models import Block, Transaction

        transactions = [Transaction.create([b.me], [([b.me], 1)])]
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
        from bigchaindb.common.exceptions import InvalidHash
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
        from bigchaindb.common.crypto import hash_data
        from bigchaindb.common.exceptions import InvalidSignature
        from bigchaindb.common.utils import gen_timestamp, serialize
        from bigchaindb.models import Block, Transaction

        transactions = [Transaction.create([b.me], [([b.me], 1)])]
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
        from bigchaindb.models import Block, Transaction

        transactions = [Transaction.create([b.me], [([b.me], 1)])]

        assert Block() != 'invalid comparison'
        assert Block(transactions) == Block(transactions)

    def test_sign_block(self, b):
        from bigchaindb.common.crypto import PrivateKey, PublicKey
        from bigchaindb.common.utils import gen_timestamp, serialize
        from bigchaindb.models import Block, Transaction

        transactions = [Transaction.create([b.me], [([b.me], 1)])]
        timestamp = gen_timestamp()
        voters = ['Qaaa', 'Qbbb']
        expected_block = {
            'timestamp': timestamp,
            'transactions': [tx.to_dict() for tx in transactions],
            'node_pubkey': b.me,
            'voters': voters,
        }
        expected_block_serialized = serialize(expected_block).encode()
        expected = PrivateKey(b.me_private).sign(expected_block_serialized)
        block = Block(transactions, b.me, timestamp, voters)
        block = block.sign(b.me_private)
        assert block.signature == expected.decode()

        public_key = PublicKey(b.me)
        assert public_key.verify(expected_block_serialized, block.signature)
