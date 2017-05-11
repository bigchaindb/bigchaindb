import pytest
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
        from bigchaindb.models import Block

        block = Block([])
        with raises(ValueError):
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

    def test_block_invalid_signature(self, b):
        from bigchaindb.common.crypto import hash_data
        from bigchaindb.common.exceptions import InvalidSignature
        from bigchaindb.common.utils import gen_timestamp, serialize
        from bigchaindb.models import Block, Transaction

        transactions = [Transaction.create([b.me], [([b.me], 1)])]
        timestamp = gen_timestamp()

        block = {
            'timestamp': timestamp,
            'transactions': [tx.to_dict() for tx in transactions],
            'node_pubkey': b.me,
            'voters': list(b.federation),
        }

        block_body = {
            'id': hash_data(serialize(block)),
            'block': block,
            'signature': 'an invalid signature',
        }

        with raises(InvalidSignature):
            Block.from_dict(block_body).validate(b)

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

    def test_block_dupe_tx(self, b):
        from bigchaindb.models import Transaction
        from bigchaindb.common.exceptions import DuplicateTransaction
        tx = Transaction.create([b.me], [([b.me], 1)])
        block = b.create_block([tx, tx])
        with raises(DuplicateTransaction):
            block._validate_block(b)

    def test_decouple_assets(self, b):
        from bigchaindb.models import Block, Transaction

        assets = [
            {'msg': '1'},
            {'msg': '2'},
            {'msg': '3'},
        ]

        txs = []
        # create 3 assets
        for asset in assets:
            tx = Transaction.create([b.me], [([b.me], 1)], asset=asset)
            txs.append(tx)

        # create a `TRANSFER` transaction.
        # the asset in `TRANSFER` transactions is not extracted
        tx = Transaction.transfer(txs[0].to_inputs(), [([b.me], 1)],
                                  asset_id=txs[0].id)
        txs.append(tx)

        # create the block
        block = Block(txs)
        # decouple assets
        assets_from_block, block_dict = block.decouple_assets()

        assert len(assets_from_block) == 3
        for i in range(3):
            assert assets_from_block[i]['data'] == assets[i]
            assert assets_from_block[i]['id'] == txs[i].id

        # check the `TRANSFER` transaction was not changed
        assert block.transactions[3].to_dict() == \
            block_dict['block']['transactions'][3]

    def test_couple_assets(self, b):
        from bigchaindb.models import Block, Transaction

        assets = [
            {'msg': '1'},
            {'msg': '2'},
            {'msg': '3'},
        ]

        txs = []
        # create 3 assets
        for asset in assets:
            tx = Transaction.create([b.me], [([b.me], 1)], asset=asset)
            txs.append(tx)

        # create a `TRANSFER` transaction.
        # the asset in `TRANSFER` transactions is not extracted
        tx = Transaction.transfer(txs[0].to_inputs(), [([b.me], 1)],
                                  asset_id=txs[0].id)
        txs.append(tx)

        # create the block
        block = Block(txs)
        # decouple assets
        assets_from_block, block_dict = block.decouple_assets()

        # reconstruct the block
        block_dict_reconstructed = Block.couple_assets(block_dict,
                                                       assets_from_block)

        # check that the reconstructed block is the as the original block
        assert block == Block.from_dict(block_dict_reconstructed)

    def test_get_asset_ids(self, b):
        from bigchaindb.models import Block, Transaction

        assets = [
            {'msg': '1'},
            {'msg': '2'},
            {'msg': '3'},
        ]

        txs = []
        # create 3 assets
        for asset in assets:
            tx = Transaction.create([b.me], [([b.me], 1)], asset=asset)
            txs.append(tx)

        # create a `TRANSFER` transaction.
        # the asset in `TRANSFER` transactions is not extracted
        tx = Transaction.transfer(txs[0].to_inputs(), [([b.me], 1)],
                                  asset_id=txs[0].id)
        txs.append(tx)

        # create the block
        block = Block(txs)
        # decouple assets
        assets_from_block, block_dict = block.decouple_assets()

        # get the asset_ids and check that they are the same as the `CREATE`
        # transactions
        asset_ids = Block.get_asset_ids(block_dict)
        assert asset_ids == [tx.id for tx in txs[:-1]]

    @pytest.mark.bdb
    def test_from_db(self, b):
        from bigchaindb.models import Block, Transaction

        assets = [
            {'msg': '1'},
            {'msg': '2'},
            {'msg': '3'},
        ]

        txs = []
        # create 3 assets
        for asset in assets:
            tx = Transaction.create([b.me], [([b.me], 1)], asset=asset)
            txs.append(tx)

        # create a `TRANSFER` transaction.
        # the asset in `TRANSFER` transactions is not extracted
        tx = Transaction.transfer(txs[0].to_inputs(), [([b.me], 1)],
                                  asset_id=txs[0].id)
        txs.append(tx)

        # create the block
        block = Block(txs)
        # decouple assets
        assets_from_block, block_dict = block.decouple_assets()

        # write the assets and block separatedly
        b.write_assets(assets_from_block)
        b.write_block(block)

        # check the reconstructed block is the same as the original block
        block_from_db = Block.from_db(b, block_dict)
        assert block == block_from_db
