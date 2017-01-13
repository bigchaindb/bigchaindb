import pytest

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


def test_get_txids_by_asset_id(signed_create_tx, signed_transfer_tx):
    from bigchaindb.backend import connect, query
    from bigchaindb.models import Block
    conn = connect()

    # create and insert two blocks, one for the create and one for the
    # transfer transaction
    block = Block(transactions=[signed_create_tx])
    conn.db.bigchain.insert_one(block.to_dict())
    block = Block(transactions=[signed_transfer_tx])
    conn.db.bigchain.insert_one(block.to_dict())

    txids = list(query.get_txids_by_asset_id(conn, signed_create_tx.id))

    assert len(txids) == 2
    assert txids == [signed_create_tx.id, signed_transfer_tx.id]


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


def test_get_owned_ids(signed_create_tx, user_pk):
    from bigchaindb.backend import connect, query
    from bigchaindb.models import Block
    conn = connect()

    # create and insert a block
    block = Block(transactions=[signed_create_tx])
    conn.db.bigchain.insert_one(block.to_dict())

    owned_ids = list(query.get_owned_ids(conn, user_pk))

    assert len(owned_ids) == 1
    assert owned_ids[0] == signed_create_tx.to_dict()


def test_get_votes_by_block_id(signed_create_tx, structurally_valid_vote):
    from bigchaindb.backend import connect, query
    from bigchaindb.models import Block
    conn = connect()

    # create and insert a block
    block = Block(transactions=[signed_create_tx])
    conn.db.bigchain.insert_one(block.to_dict())
    # create and insert some votes
    structurally_valid_vote['vote']['voting_for_block'] = block.id
    conn.db.votes.insert_one(structurally_valid_vote)
    structurally_valid_vote['vote']['voting_for_block'] = block.id
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
    query.write_block(conn, block)

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


def test_has_transaction(signed_create_tx):
    from bigchaindb.backend import connect, query
    from bigchaindb.models import Block
    conn = connect()

    # create and insert block
    block = Block(transactions=[signed_create_tx])
    conn.db.bigchain.insert_one(block.to_dict())

    assert query.has_transaction(conn, signed_create_tx.id)
    assert query.has_transaction(conn, 'aaa') is False


def test_count_blocks(signed_create_tx):
    from bigchaindb.backend import connect, query
    from bigchaindb.models import Block
    conn = connect()

    # create and insert some blocks
    block = Block(transactions=[signed_create_tx])
    conn.db.bigchain.insert_one(block.to_dict())
    conn.db.bigchain.insert_one(block.to_dict())

    assert query.count_blocks(conn) == 2


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
        {'node_pubkey': structurally_valid_vote['node_pubkey']}
    )

    assert vote_db == structurally_valid_vote


def test_get_genesis_block(genesis_block):
    from bigchaindb.backend import connect, query
    conn = connect()

    assert query.get_genesis_block(conn) == genesis_block.to_dict()


def test_get_last_voted_block(genesis_block, signed_create_tx, b):
    from bigchaindb.backend import connect, query
    from bigchaindb.models import Block
    from bigchaindb.common.exceptions import CyclicBlockchainError
    conn = connect()

    # check that the last voted block is the genesis block
    assert query.get_last_voted_block(conn, b.me) == genesis_block.to_dict()

    # create and insert a new vote and block
    block = Block(transactions=[signed_create_tx])
    conn.db.bigchain.insert_one(block.to_dict())
    vote = b.vote(block.id, genesis_block.id, True)
    conn.db.votes.insert_one(vote)

    assert query.get_last_voted_block(conn, b.me) == block.to_dict()

    # force a bad chain
    vote.pop('_id')
    vote['vote']['voting_for_block'] = genesis_block.id
    vote['vote']['previous_block'] = block.id
    conn.db.votes.insert_one(vote)

    with pytest.raises(CyclicBlockchainError):
        query.get_last_voted_block(conn, b.me)


def test_get_unvoted_blocks(signed_create_tx):
    from bigchaindb.backend import connect, query
    from bigchaindb.models import Block
    conn = connect()

    # create and insert a block
    block = Block(transactions=[signed_create_tx], node_pubkey='aaa')
    conn.db.bigchain.insert_one(block.to_dict())

    unvoted_blocks = list(query.get_unvoted_blocks(conn, 'aaa'))

    assert len(unvoted_blocks) == 1
    assert unvoted_blocks[0] == block.to_dict()
