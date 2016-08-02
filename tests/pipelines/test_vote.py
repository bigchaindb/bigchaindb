from unittest.mock import patch
import rethinkdb as r
from multipipes import Pipe, Pipeline

from bigchaindb import util
from bigchaindb import crypto


def dummy_tx(b):
    tx = b.create_transaction(b.me, b.me, None, 'CREATE')
    tx_signed = b.sign_transaction(tx, b.me_private)
    return tx_signed


def dummy_block(b):
    block = b.create_block([dummy_tx(b) for _ in range(10)])
    return block


def test_vote_ungroup_returns_a_set_of_results(b):
    from bigchaindb.pipelines import vote

    b.create_genesis_block()
    block = dummy_block(b)
    vote_obj = vote.Vote()
    txs = list(vote_obj.ungroup(block))

    assert len(txs) == 10


def test_vote_validate_transaction(b):
    from bigchaindb.pipelines import vote

    b.create_genesis_block()
    tx = dummy_tx(b)
    vote_obj = vote.Vote()
    validation = vote_obj.validate_tx(tx, 123, 1)
    assert validation == (True, 123, 1)

    tx['id'] = 'a' * 64
    validation = vote_obj.validate_tx(tx, 456, 10)
    assert validation == (False, 456, 10)


def test_vote_accumulates_transactions(b):
    from bigchaindb.pipelines import vote

    b.create_genesis_block()
    vote_obj = vote.Vote()

    for _ in range(10):
        tx = dummy_tx(b)

    validation = vote_obj.validate_tx(tx, 123, 1)
    assert validation == (True, 123, 1)

    tx['id'] = 'a' * 64
    validation = vote_obj.validate_tx(tx, 456, 10)
    assert validation == (False, 456, 10)


def test_valid_block_voting_sequential(b, monkeypatch):
    from bigchaindb.pipelines import vote

    monkeypatch.setattr(util, 'timestamp', lambda: '1')
    genesis = b.create_genesis_block()
    vote_obj = vote.Vote()
    block = dummy_block(b)

    for tx, block_id, num_tx in vote_obj.ungroup(block):
        last_vote = vote_obj.vote(*vote_obj.validate_tx(tx, block_id, num_tx))

    vote_obj.write_vote(last_vote)
    vote_rs = r.table('votes').get_all([block['id'], b.me],
                                       index='block_and_voter').run(b.conn)
    vote_doc = vote_rs.next()

    assert vote_doc['vote'] == {'voting_for_block': block['id'],
                                'previous_block': genesis['id'],
                                'is_block_valid': True,
                                'invalid_reason': None,
                                'timestamp': '1'}

    assert vote_doc['node_pubkey'] == b.me
    assert crypto.VerifyingKey(b.me).verify(util.serialize(vote_doc['vote']),
                                            vote_doc['signature']) is True


def test_valid_block_voting_multiprocessing(b, monkeypatch):
    from bigchaindb.pipelines import vote

    inpipe = Pipe()
    outpipe = Pipe()

    monkeypatch.setattr(util, 'timestamp', lambda: '1')
    genesis = b.create_genesis_block()
    vote_pipeline = vote.create_pipeline()
    vote_pipeline.setup(indata=inpipe, outdata=outpipe)

    block = dummy_block(b)

    inpipe.put(block)
    vote_pipeline.start()
    vote_out = outpipe.get()
    vote_pipeline.terminate()

    vote_rs = r.table('votes').get_all([block['id'], b.me],
                                       index='block_and_voter').run(b.conn)
    vote_doc = vote_rs.next()
    assert vote_out['vote'] == vote_doc['vote']
    assert vote_doc['vote'] == {'voting_for_block': block['id'],
                                'previous_block': genesis['id'],
                                'is_block_valid': True,
                                'invalid_reason': None,
                                'timestamp': '1'}

    assert vote_doc['node_pubkey'] == b.me
    assert crypto.VerifyingKey(b.me).verify(util.serialize(vote_doc['vote']),
                                            vote_doc['signature']) is True


def test_valid_block_voting_with_create_transaction(b, monkeypatch):
    from bigchaindb.pipelines import vote

    genesis = b.create_genesis_block()

    # create a `CREATE` transaction
    test_user_priv, test_user_pub = crypto.generate_key_pair()
    tx = b.create_transaction(b.me, test_user_pub, None, 'CREATE')
    tx_signed = b.sign_transaction(tx, b.me_private)

    monkeypatch.setattr(util, 'timestamp', lambda: '1')
    block = b.create_block([tx_signed])

    inpipe = Pipe()
    outpipe = Pipe()

    vote_pipeline = vote.create_pipeline()
    vote_pipeline.setup(indata=inpipe, outdata=outpipe)

    inpipe.put(block)
    vote_pipeline.start()
    vote_out = outpipe.get()
    vote_pipeline.terminate()

    vote_rs = r.table('votes').get_all([block['id'], b.me],
                                       index='block_and_voter').run(b.conn)
    vote_doc = vote_rs.next()
    assert vote_out['vote'] == vote_doc['vote']
    assert vote_doc['vote'] == {'voting_for_block': block['id'],
                                'previous_block': genesis['id'],
                                'is_block_valid': True,
                                'invalid_reason': None,
                                'timestamp': '1'}

    assert vote_doc['node_pubkey'] == b.me
    assert crypto.VerifyingKey(b.me).verify(util.serialize(vote_doc['vote']),
                                            vote_doc['signature']) is True

def test_valid_block_voting_with_transfer_transactions(monkeypatch, b):
    from bigchaindb.pipelines import vote

    genesis = b.create_genesis_block()

    # create a `CREATE` transaction
    test_user_priv, test_user_pub = crypto.generate_key_pair()
    tx = b.create_transaction(b.me, test_user_pub, None, 'CREATE')
    tx_signed = b.sign_transaction(tx, b.me_private)

    monkeypatch.setattr(util, 'timestamp', lambda: '1')
    block = b.create_block([tx_signed])
    b.write_block(block, durability='hard')

    # create a `TRANSFER` transaction
    test_user2_priv, test_user2_pub = crypto.generate_key_pair()
    tx2 = b.create_transaction(test_user_pub, test_user2_pub,
                               {'txid': tx['id'], 'cid': 0}, 'TRANSFER')
    tx2_signed = b.sign_transaction(tx2, test_user_priv)

    monkeypatch.setattr(util, 'timestamp', lambda: '2')
    block2 = b.create_block([tx2_signed])
    b.write_block(block2, durability='hard')

    inpipe = Pipe()
    outpipe = Pipe()

    vote_pipeline = vote.create_pipeline()
    vote_pipeline.setup(indata=inpipe, outdata=outpipe)

    inpipe.put(block)
    inpipe.put(block2)
    vote_pipeline.start()
    vote_out = outpipe.get()
    vote2_out = outpipe.get()
    vote_pipeline.terminate()

    vote_rs = r.table('votes').get_all([block['id'], b.me],
                                       index='block_and_voter').run(b.conn)
    vote_doc = vote_rs.next()
    assert vote_out['vote'] == vote_doc['vote']
    assert vote_doc['vote'] == {'voting_for_block': block['id'],
                                'previous_block': genesis['id'],
                                'is_block_valid': True,
                                'invalid_reason': None,
                                'timestamp': '2'}

    assert vote_doc['node_pubkey'] == b.me
    assert crypto.VerifyingKey(b.me).verify(util.serialize(vote_doc['vote']),
                                            vote_doc['signature']) is True

    vote2_rs = r.table('votes').get_all([block2['id'], b.me],
                                        index='block_and_voter').run(b.conn)
    vote2_doc = vote2_rs.next()
    assert vote2_out['vote'] == vote2_doc['vote']
    assert vote2_doc['vote'] == {'voting_for_block': block2['id'],
                                 'previous_block': block['id'],
                                 'is_block_valid': True,
                                 'invalid_reason': None,
                                 'timestamp': '2'}

    assert vote2_doc['node_pubkey'] == b.me
    assert crypto.VerifyingKey(b.me).verify(util.serialize(vote2_doc['vote']),
                                            vote2_doc['signature']) is True


def test_invalid_block_voting(monkeypatch, b, user_vk):
    from bigchaindb.pipelines import vote

    inpipe = Pipe()
    outpipe = Pipe()

    monkeypatch.setattr(util, 'timestamp', lambda: '1')
    genesis = b.create_genesis_block()
    vote_pipeline = vote.create_pipeline()
    vote_pipeline.setup(indata=inpipe, outdata=outpipe)

    block = dummy_block(b)
    block['block']['transactions'][0]['id'] = 'abc'

    inpipe.put(block)
    vote_pipeline.start()
    vote_out = outpipe.get()
    vote_pipeline.terminate()

    vote_rs = r.table('votes').get_all([block['id'], b.me],
                                       index='block_and_voter').run(b.conn)
    vote_doc = vote_rs.next()
    assert vote_out['vote'] == vote_doc['vote']
    assert vote_doc['vote'] == {'voting_for_block': block['id'],
                                'previous_block': genesis['id'],
                                'is_block_valid': False,
                                'invalid_reason': None,
                                'timestamp': '1'}

    assert vote_doc['node_pubkey'] == b.me
    assert crypto.VerifyingKey(b.me).verify(util.serialize(vote_doc['vote']),
                                            vote_doc['signature']) is True


@patch.object(Pipeline, 'start')
def test_start(mock_start, b):
    # TODO: `block.start` is just a wrapper around `vote.create_pipeline`,
    #       that is tested by `test_full_pipeline`.
    #       If anyone has better ideas on how to test this, please do a PR :)
    from bigchaindb.pipelines import vote

    genesis = b.create_genesis_block()

    vote.start()
    mock_start.assert_called_with()
