from copy import deepcopy

import pytest
from unittest import mock
import pymongo

pytestmark = pytest.mark.bdb


def test_write_transaction(signed_create_tx):
    from bigchaindb.backend import connect, query
    conn = connect()

    # write the transaction
    query.write_transaction(conn, signed_create_tx.to_dict())

    # get the transaction
    tx_db = conn.db.backlog.find_one({'id': signed_create_tx.id},
                                     {'_id': False})

    assert tx_db == signed_create_tx.to_dict()


def test_update_transaction(signed_create_tx):
    from bigchaindb.backend import connect, query
    conn = connect()

    # update_transaction can update any field we want, but lets update the
    # same fields that are updated by bigchaindb core.
    signed_create_tx = signed_create_tx.to_dict()
    signed_create_tx.update({'assignee': 'aaa', 'assignment_timestamp': 10})
    conn.db.backlog.insert_one(signed_create_tx)

    query.update_transaction(conn, signed_create_tx['id'],
                             {'assignee': 'bbb', 'assignment_timestamp': 20})

    tx_db = conn.db.backlog.find_one({'id': signed_create_tx['id']},
                                     {'_id': False})

    assert tx_db['assignee'] == 'bbb'
    assert tx_db['assignment_timestamp'] == 20


def test_delete_transaction(signed_create_tx):
    from bigchaindb.backend import connect, query
    conn = connect()

    # write_the transaction
    result = conn.db.backlog.insert_one(signed_create_tx.to_dict())

    # delete transaction
    query.delete_transaction(conn, signed_create_tx.id)

    tx_db = conn.db.backlog.find_one({'_id': result.inserted_id})
    assert tx_db is None


def test_get_stale_transactions(signed_create_tx):
    import time
    from bigchaindb.backend import connect, query
    conn = connect()

    # create two transaction, one of them stale
    tx1 = signed_create_tx.to_dict()
    tx1.update({'id': 'notstale', 'assignment_timestamp': time.time()})
    tx2 = signed_create_tx.to_dict()
    tx2.update({'id': 'stale', 'assignment_timestamp': time.time() - 60})

    # write the transactions
    conn.db.backlog.insert_one(tx1)
    conn.db.backlog.insert_one(tx2)

    # get stale transactions
    stale_txs = list(query.get_stale_transactions(conn, 30))

    assert len(stale_txs) == 1
    assert stale_txs[0]['id'] == 'stale'


def test_get_transaction_from_block(user_pk):
    from bigchaindb.backend import connect, query
    from bigchaindb.models import Transaction, Block
    conn = connect()

    # create a block with 2 transactions
    txs = [
        Transaction.create([user_pk], [([user_pk], 1)]),
        Transaction.create([user_pk], [([user_pk], 1)]),
    ]
    block = Block(transactions=txs)
    conn.db.bigchain.insert_one(block.to_dict())

    tx_db = query.get_transaction_from_block(conn, txs[0].id, block.id)
    assert tx_db == txs[0].to_dict()

    assert query.get_transaction_from_block(conn, txs[0].id, 'aaa') is None
    assert query.get_transaction_from_block(conn, 'aaa', block.id) is None


def test_get_transaction_from_backlog(create_tx):
    from bigchaindb.backend import connect, query
    conn = connect()

    # insert transaction
    conn.db.backlog.insert_one(create_tx.to_dict())

    # query the backlog
    tx_db = query.get_transaction_from_backlog(conn, create_tx.id)

    assert tx_db == create_tx.to_dict()


def test_get_block_status_from_transaction(create_tx):
    from bigchaindb.backend import connect, query
    from bigchaindb.models import Block
    conn = connect()

    # create a block
    block = Block(transactions=[create_tx], voters=['aaa', 'bbb', 'ccc'])
    # insert block
    conn.db.bigchain.insert_one(block.to_dict())

    block_db = list(query.get_blocks_status_from_transaction(conn,
                                                             create_tx.id))

    assert len(block_db) == 1
    block_db = block_db.pop()
    assert block_db['id'] == block.id
    assert block_db['block']['voters'] == block.voters


def test_get_asset_by_id(create_tx):
    from bigchaindb.backend import connect, query
    from bigchaindb.models import Block
    conn = connect()

    # create asset and block
    create_tx.asset = {'msg': 'aaa'}
    block = Block(transactions=[create_tx])
    conn.db.bigchain.insert_one(block.to_dict())

    asset = list(query.get_asset_by_id(conn, create_tx.id))

    assert len(asset) == 1
    assert asset[0]['asset'] == create_tx.asset


def test_get_spent(signed_create_tx, signed_transfer_tx):
    from bigchaindb.backend import connect, query
    from bigchaindb.models import Block
    conn = connect()

    # create and insert two blocks, one for the create and one for the
    # transfer transaction
    block = Block(transactions=[signed_create_tx])
    conn.db.bigchain.insert_one(block.to_dict())
    block = Block(transactions=[signed_transfer_tx])
    conn.db.bigchain.insert_one(block.to_dict())

    spents = list(query.get_spent(conn, signed_create_tx.id, 0))

    assert len(spents) == 1
    assert spents[0] == signed_transfer_tx.to_dict()


def test_get_spent_for_tx_with_multiple_inputs(carol):
    from bigchaindb.backend import connect, query
    from bigchaindb.models import Block, Transaction
    conn = connect()
    tx_0 = Transaction.create(
        [carol.public_key],
        [([carol.public_key], 1),
         ([carol.public_key], 1),
         ([carol.public_key], 2)],
    ).sign([carol.private_key])
    block = Block(transactions=[tx_0])
    conn.db.bigchain.insert_one(block.to_dict())
    spents = list(query.get_spent(conn, tx_0.id, 0))
    assert not spents

    tx_1 = Transaction.transfer(
        tx_0.to_inputs()[2:3],
        [([carol.public_key], 1),
         ([carol.public_key], 1)],
        asset_id=tx_0.id,
    ).sign([carol.private_key])
    block = Block(transactions=[tx_1])
    conn.db.bigchain.insert_one(block.to_dict())
    spents = list(query.get_spent(conn, tx_0.id, 0))
    assert not spents

    tx_2 = Transaction.transfer(
        tx_0.to_inputs()[0:1] + tx_1.to_inputs()[1:2],
        [([carol.public_key], 2)],
        asset_id=tx_0.id,
    ).sign([carol.private_key])
    block = Block(transactions=[tx_2])
    conn.db.bigchain.insert_one(block.to_dict())
    spents = list(query.get_spent(conn, tx_0.id, 1))
    assert not spents


def test_get_owned_ids(signed_create_tx, user_pk):
    from bigchaindb.backend import connect, query
    from bigchaindb.models import Block
    conn = connect()

    # create and insert a block
    block = Block(transactions=[signed_create_tx])
    conn.db.bigchain.insert_one(block.to_dict())

    [(block_id, tx)] = list(query.get_owned_ids(conn, user_pk))

    assert block_id == block.id
    assert tx == signed_create_tx.to_dict()


def test_get_votes_by_block_id(signed_create_tx, structurally_valid_vote):
    from bigchaindb.common.crypto import generate_key_pair
    from bigchaindb.backend import connect, query
    from bigchaindb.models import Block
    conn = connect()

    # create and insert a block
    block = Block(transactions=[signed_create_tx])
    conn.db.bigchain.insert_one(block.to_dict())

    # create and insert some votes
    structurally_valid_vote['vote']['voting_for_block'] = block.id
    conn.db.votes.insert_one(structurally_valid_vote)
    # create a second vote under a different key
    _, pk = generate_key_pair()
    structurally_valid_vote['vote']['voting_for_block'] = block.id
    structurally_valid_vote['node_pubkey'] = pk
    structurally_valid_vote.pop('_id')
    conn.db.votes.insert_one(structurally_valid_vote)

    votes = list(query.get_votes_by_block_id(conn, block.id))

    assert len(votes) == 2
    assert votes[0]['vote']['voting_for_block'] == block.id
    assert votes[1]['vote']['voting_for_block'] == block.id


def test_get_votes_by_block_id_and_voter(signed_create_tx,
                                         structurally_valid_vote):
    from bigchaindb.backend import connect, query
    from bigchaindb.models import Block
    conn = connect()

    # create and insert a block
    block = Block(transactions=[signed_create_tx])
    conn.db.bigchain.insert_one(block.to_dict())
    # create and insert some votes
    structurally_valid_vote['vote']['voting_for_block'] = block.id
    structurally_valid_vote['node_pubkey'] = 'aaa'
    conn.db.votes.insert_one(structurally_valid_vote)
    structurally_valid_vote['vote']['voting_for_block'] = block.id
    structurally_valid_vote['node_pubkey'] = 'bbb'
    structurally_valid_vote.pop('_id')
    conn.db.votes.insert_one(structurally_valid_vote)

    votes = list(query.get_votes_by_block_id_and_voter(conn, block.id, 'aaa'))

    assert len(votes) == 1
    assert votes[0]['node_pubkey'] == 'aaa'


def test_write_block(signed_create_tx):
    from bigchaindb.backend import connect, query
    from bigchaindb.models import Block
    conn = connect()

    # create and write block
    block = Block(transactions=[signed_create_tx])
    query.write_block(conn, block.to_dict())

    block_db = conn.db.bigchain.find_one({'id': block.id}, {'_id': False})

    assert block_db == block.to_dict()


def test_get_block(signed_create_tx):
    from bigchaindb.backend import connect, query
    from bigchaindb.models import Block
    conn = connect()

    # create and insert block
    block = Block(transactions=[signed_create_tx])
    conn.db.bigchain.insert_one(block.to_dict())

    block_db = query.get_block(conn, block.id)

    assert block_db == block.to_dict()


def test_count_blocks(signed_create_tx):
    from bigchaindb.backend import connect, query
    from bigchaindb.models import Block
    conn = connect()

    assert query.count_blocks(conn) == 0

    # create and insert some blocks
    block = Block(transactions=[signed_create_tx])
    conn.db.bigchain.insert_one(block.to_dict())

    assert query.count_blocks(conn) == 1


def test_count_backlog(signed_create_tx):
    from bigchaindb.backend import connect, query
    conn = connect()

    # create and insert some transations
    conn.db.backlog.insert_one(signed_create_tx.to_dict())
    signed_create_tx.metadata = {'msg': 'aaa'}
    conn.db.backlog.insert_one(signed_create_tx.to_dict())

    assert query.count_backlog(conn) == 2


def test_write_vote(structurally_valid_vote):
    from bigchaindb.backend import connect, query
    conn = connect()

    # write a vote
    query.write_vote(conn, structurally_valid_vote)
    # retrieve the vote
    vote_db = conn.db.votes.find_one(
        {'node_pubkey': structurally_valid_vote['node_pubkey']},
        {'_id': False}
    )

    assert vote_db == structurally_valid_vote


def test_duplicate_vote_raises_duplicate_key(structurally_valid_vote):
    from bigchaindb.backend import connect, query
    from bigchaindb.backend.exceptions import DuplicateKeyError
    conn = connect()

    # write a vote
    query.write_vote(conn, structurally_valid_vote)

    # write the same vote a second time
    with pytest.raises(DuplicateKeyError):
        query.write_vote(conn, structurally_valid_vote)


def test_get_genesis_block(genesis_block):
    from bigchaindb.backend import connect, query
    conn = connect()

    assets, genesis_block_dict = genesis_block.decouple_assets()
    metadata, genesis_block_dict = genesis_block.decouple_metadata(genesis_block_dict)
    assert query.get_genesis_block(conn) == genesis_block_dict


def test_get_last_voted_block_id(genesis_block, signed_create_tx, b):
    from bigchaindb.backend import connect, query
    from bigchaindb.models import Block
    from bigchaindb.common.exceptions import CyclicBlockchainError
    conn = connect()

    # check that the last voted block is the genesis block
    assert query.get_last_voted_block_id(conn, b.me) == genesis_block.id

    # create and insert a new vote and block
    block = Block(transactions=[signed_create_tx])
    conn.db.bigchain.insert_one(block.to_dict())
    vote = b.vote(block.id, genesis_block.id, True)
    conn.db.votes.insert_one(vote)

    assert query.get_last_voted_block_id(conn, b.me) == block.id

    # force a bad chain
    vote.pop('_id')
    vote['vote']['voting_for_block'] = genesis_block.id
    vote['vote']['previous_block'] = block.id
    conn.db.votes.insert_one(vote)

    with pytest.raises(CyclicBlockchainError):
        query.get_last_voted_block_id(conn, b.me)


def test_get_txids_filtered(signed_create_tx, signed_transfer_tx):
    from bigchaindb.backend import connect, query
    from bigchaindb.models import Block, Transaction
    conn = connect()

    # create and insert two blocks, one for the create and one for the
    # transfer transaction
    block = Block(transactions=[signed_create_tx])
    conn.db.bigchain.insert_one(block.to_dict())
    block = Block(transactions=[signed_transfer_tx])
    conn.db.bigchain.insert_one(block.to_dict())

    asset_id = Transaction.get_asset_id([signed_create_tx, signed_transfer_tx])

    # Test get by just asset id
    txids = set(query.get_txids_filtered(conn, asset_id))
    assert txids == {signed_create_tx.id, signed_transfer_tx.id}

    # Test get by asset and CREATE
    txids = set(query.get_txids_filtered(conn, asset_id, Transaction.CREATE))
    assert txids == {signed_create_tx.id}

    # Test get by asset and TRANSFER
    txids = set(query.get_txids_filtered(conn, asset_id, Transaction.TRANSFER))
    assert txids == {signed_transfer_tx.id}


@mock.patch('bigchaindb.backend.mongodb.changefeed._FEED_STOP', True)
def test_get_new_blocks_feed(b, create_tx):
    from bigchaindb.backend import query
    from bigchaindb.models import Block
    import random

    def create_block():
        ts = str(random.random())
        block = Block(transactions=[create_tx], timestamp=ts)
        b.write_block(block)
        block_dict = block.decouple_assets()[1]
        return block.decouple_metadata(block_dict)[1]

    create_block()
    b1 = create_block()
    b2 = create_block()

    feed = query.get_new_blocks_feed(b.connection, b1['id'])

    assert feed.__next__() == b2

    b3 = create_block()

    assert list(feed) == [b3]


def test_get_spending_transactions(user_pk):
    from bigchaindb.backend import connect, query
    from bigchaindb.models import Block, Transaction
    conn = connect()

    out = [([user_pk], 1)]
    tx1 = Transaction.create([user_pk], out * 3)
    inputs = tx1.to_inputs()
    tx2 = Transaction.transfer([inputs[0]], out, tx1.id)
    tx3 = Transaction.transfer([inputs[1]], out, tx1.id)
    tx4 = Transaction.transfer([inputs[2]], out, tx1.id)
    block = Block([tx1, tx2, tx3, tx4])
    conn.db.bigchain.insert_one(block.to_dict())

    links = [inputs[0].fulfills.to_dict(), inputs[2].fulfills.to_dict()]
    res = list(query.get_spending_transactions(conn, links))

    # tx3 not a member because input 1 not asked for
    assert res == [(block.id, tx2.to_dict()), (block.id, tx4.to_dict())]


def test_get_votes_for_blocks_by_voter():
    from bigchaindb.backend import connect, query

    conn = connect()
    votes = [
        {
            'node_pubkey': 'a',
            'vote': {'voting_for_block': 'block1'},
        },
        {
            'node_pubkey': 'b',
            'vote': {'voting_for_block': 'block1'},
        },
        {
            'node_pubkey': 'a',
            'vote': {'voting_for_block': 'block2'},
        },
        {
            'node_pubkey': 'a',
            'vote': {'voting_for_block': 'block3'},
        }
    ]
    for vote in votes:
        conn.db.votes.insert_one(vote.copy())
    res = query.get_votes_for_blocks_by_voter(conn, ['block1', 'block2'], 'a')
    assert list(res) == [votes[0], votes[2]]


def test_write_assets():
    from bigchaindb.backend import connect, query
    conn = connect()

    assets = [
        {'id': 1, 'data': '1'},
        {'id': 2, 'data': '2'},
        {'id': 3, 'data': '3'},
        # Duplicated id. Should not be written to the database
        {'id': 1, 'data': '1'},
    ]

    # write the assets
    query.write_assets(conn, deepcopy(assets))

    # check that 3 assets were written to the database
    cursor = conn.db.assets.find({}, projection={'_id': False})\
                           .sort('id', pymongo.ASCENDING)

    assert cursor.count() == 3
    assert list(cursor) == assets[:-1]


def test_get_assets():
    from bigchaindb.backend import connect, query
    conn = connect()

    assets = [
        {'id': 1, 'data': '1'},
        {'id': 2, 'data': '2'},
        {'id': 3, 'data': '3'},
    ]

    # write the assets
    conn.db.assets.insert_many(deepcopy(assets), ordered=False)

    # read only 2 assets
    cursor = query.get_assets(conn, [1, 3])

    assert cursor.count() == 2
    assert list(cursor.sort('id', pymongo.ASCENDING)) == assets[::2]


def test_text_search():
    from bigchaindb.backend import connect, query
    conn = connect()

    # Example data and tests cases taken from the mongodb documentation
    # https://docs.mongodb.com/manual/reference/operator/query/text/
    assets = [
        {'id': 1, 'subject': 'coffee', 'author': 'xyz', 'views': 50},
        {'id': 2, 'subject': 'Coffee Shopping', 'author': 'efg', 'views': 5},
        {'id': 3, 'subject': 'Baking a cake', 'author': 'abc', 'views': 90},
        {'id': 4, 'subject': 'baking', 'author': 'xyz', 'views': 100},
        {'id': 5, 'subject': 'Café Con Leche', 'author': 'abc', 'views': 200},
        {'id': 6, 'subject': 'Сырники', 'author': 'jkl', 'views': 80},
        {'id': 7, 'subject': 'coffee and cream', 'author': 'efg', 'views': 10},
        {'id': 8, 'subject': 'Cafe con Leche', 'author': 'xyz', 'views': 10}
    ]

    # insert the assets
    conn.db.assets.insert_many(deepcopy(assets), ordered=False)

    # test search single word
    assert list(query.text_search(conn, 'coffee')) == [
        {'id': 1, 'subject': 'coffee', 'author': 'xyz', 'views': 50},
        {'id': 2, 'subject': 'Coffee Shopping', 'author': 'efg', 'views': 5},
        {'id': 7, 'subject': 'coffee and cream', 'author': 'efg', 'views': 10},
    ]

    # match any of the search terms
    assert list(query.text_search(conn, 'bake coffee cake')) == [
        {'author': 'abc', 'id': 3, 'subject': 'Baking a cake', 'views': 90},
        {'author': 'xyz', 'id': 1, 'subject': 'coffee', 'views': 50},
        {'author': 'xyz', 'id': 4, 'subject': 'baking', 'views': 100},
        {'author': 'efg', 'id': 2, 'subject': 'Coffee Shopping', 'views': 5},
        {'author': 'efg', 'id': 7, 'subject': 'coffee and cream', 'views': 10}
    ]

    # search for a phrase
    assert list(query.text_search(conn, '\"coffee shop\"')) == [
        {'id': 2, 'subject': 'Coffee Shopping', 'author': 'efg', 'views': 5},
    ]

    # exclude documents that contain a term
    assert list(query.text_search(conn, 'coffee -shop')) == [
        {'id': 1, 'subject': 'coffee', 'author': 'xyz', 'views': 50},
        {'id': 7, 'subject': 'coffee and cream', 'author': 'efg', 'views': 10},
    ]

    # search different language
    assert list(query.text_search(conn, 'leche', language='es')) == [
        {'id': 5, 'subject': 'Café Con Leche', 'author': 'abc', 'views': 200},
        {'id': 8, 'subject': 'Cafe con Leche', 'author': 'xyz', 'views': 10}
    ]

    # case and diacritic insensitive search
    assert list(query.text_search(conn, 'сы́рники CAFÉS')) == [
        {'id': 6, 'subject': 'Сырники', 'author': 'jkl', 'views': 80},
        {'id': 5, 'subject': 'Café Con Leche', 'author': 'abc', 'views': 200},
        {'id': 8, 'subject': 'Cafe con Leche', 'author': 'xyz', 'views': 10}
    ]

    # case sensitive search
    assert list(query.text_search(conn, 'Coffee', case_sensitive=True)) == [
        {'id': 2, 'subject': 'Coffee Shopping', 'author': 'efg', 'views': 5},
    ]

    # diacritic sensitive search
    assert list(query.text_search(conn, 'CAFÉ', diacritic_sensitive=True)) == [
        {'id': 5, 'subject': 'Café Con Leche', 'author': 'abc', 'views': 200},
    ]

    # return text score
    assert list(query.text_search(conn, 'coffee', text_score=True)) == [
        {'id': 1, 'subject': 'coffee', 'author': 'xyz', 'views': 50, 'score': 1.0},
        {'id': 2, 'subject': 'Coffee Shopping', 'author': 'efg', 'views': 5, 'score': 0.75},
        {'id': 7, 'subject': 'coffee and cream', 'author': 'efg', 'views': 10, 'score': 0.75},
    ]

    # limit search result
    assert list(query.text_search(conn, 'coffee', limit=2)) == [
        {'id': 1, 'subject': 'coffee', 'author': 'xyz', 'views': 50},
        {'id': 2, 'subject': 'Coffee Shopping', 'author': 'efg', 'views': 5},
    ]
