import os

import pytest

from bigchaindb import backend


pytestmark = pytest.mark.tendermint


def test_asset_is_separated_from_transaciton(b):
    from bigchaindb.models import Transaction
    from bigchaindb.common.crypto import generate_key_pair

    alice = generate_key_pair()
    bob = generate_key_pair()

    asset = {'Never gonna': ['give you up',
                             'let you down',
                             'run around'
                             'desert you',
                             'make you cry',
                             'say goodbye',
                             'tell a lie',
                             'hurt you']}

    tx = Transaction.create([alice.public_key],
                            [([bob.public_key], 1)],
                            metadata=None,
                            asset=asset)\
                    .sign([alice.private_key])

    b.store_transaction(tx)
    assert 'asset' not in backend.query.get_transaction(b.connection, tx.id)
    assert backend.query.get_asset(b.connection, tx.id)['data'] == asset
    assert b.get_transaction(tx.id) == tx


def test_get_latest_block(b):
    from bigchaindb.tendermint.lib import Block

    for i in range(10):
        app_hash = os.urandom(16).hex()
        block = Block(app_hash=app_hash, height=i)._asdict()
        b.store_block(block)

    block = b.get_latest_block()
    assert block['height'] == 9
