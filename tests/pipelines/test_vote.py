import random
import time
from unittest.mock import patch

from multipipes import Pipe, Pipeline
import pytest


# TODO: dummy_tx and dummy_block could be fixtures
def dummy_tx(b):
    from bigchaindb.models import Transaction
    tx = Transaction.create([b.me], [([b.me], 1)],
                            metadata={'msg': random.random()})
    tx = tx.sign([b.me_private])
    return tx


def dummy_block(b):
    block = b.create_block([dummy_tx(b) for _ in range(10)])
    return block


def decouple_assets(b, block):
    # the block comming from the database does not contain the assets
    # so we need to pass the block without the assets and store the assets
    # so that the voting pipeline can reconstruct it
    assets, block_dict = block.decouple_assets()
    b.write_assets(assets)
    return block_dict


DUMMY_SHA3 = '0123456789abcdef' * 4


def test_vote_creation_valid(b):
    from bigchaindb.common import crypto
    from bigchaindb.common.utils import serialize

    # create valid block
    block = dummy_block(b)
    # retrieve vote
    vote = b.vote(block.id, DUMMY_SHA3, True)

    # assert vote is correct
    assert vote['vote']['voting_for_block'] == block.id
    assert vote['vote']['previous_block'] == DUMMY_SHA3
    assert vote['vote']['is_block_valid'] is True
    assert vote['vote']['invalid_reason'] is None
    assert vote['node_pubkey'] == b.me
    assert isinstance(vote['signature'], str)
    assert crypto.PublicKey(b.me).verify(serialize(vote['vote']).encode(),
                                         vote['signature']) is True


def test_vote_creation_invalid(b):
    from bigchaindb.common import crypto
    from bigchaindb.common.utils import serialize

    # create valid block
    block = dummy_block(b)
    # retrieve vote
    vote = b.vote(block.id, DUMMY_SHA3, False)

    # assert vote is correct
    assert vote['vote']['voting_for_block'] == block.id
    assert vote['vote']['previous_block'] == DUMMY_SHA3
    assert vote['vote']['is_block_valid'] is False
    assert vote['vote']['invalid_reason'] is None
    assert vote['node_pubkey'] == b.me
    assert crypto.PublicKey(b.me).verify(serialize(vote['vote']).encode(),
                                         vote['signature']) is True


@pytest.mark.genesis
def test_vote_ungroup_returns_a_set_of_results(b):
    from bigchaindb.pipelines import vote

    block = dummy_block(b)
    vote_obj = vote.Vote()
    txs = list(vote_obj.ungroup(block.id, block.transactions))

    assert len(txs) == 10


@pytest.mark.genesis
def test_vote_validate_block(b):
    from bigchaindb.pipelines import vote

    tx = dummy_tx(b)
    block = b.create_block([tx])
    block_dict = decouple_assets(b, block)

    vote_obj = vote.Vote()
    validation = vote_obj.validate_block(block_dict)
    assert validation[0] == block.id
    for tx1, tx2 in zip(validation[1], block.transactions):
        assert tx1 == tx2

    block = b.create_block([tx])
    # NOTE: Setting a blocks signature to `None` invalidates it.
    block.signature = None

    vote_obj = vote.Vote()
    validation = vote_obj.validate_block(block.to_dict())
    assert validation[0] == block.id
    for tx1, tx2 in zip(validation[1], [vote_obj.invalid_dummy_tx]):
        assert tx1 == tx2


@pytest.mark.genesis
def test_validate_block_with_invalid_id(b):
    from bigchaindb.pipelines import vote

    tx = dummy_tx(b)
    block = b.create_block([tx]).to_dict()
    block['id'] = 'an invalid id'

    vote_obj = vote.Vote()
    block_id, invalid_dummy_tx = vote_obj.validate_block(block)
    assert block_id == block['id']
    assert invalid_dummy_tx == [vote_obj.invalid_dummy_tx]


@pytest.mark.genesis
def test_validate_block_with_duplicated_transactions(b):
    from bigchaindb.pipelines import vote

    tx = dummy_tx(b)
    block = b.create_block([tx, tx]).to_dict()

    vote_obj = vote.Vote()
    block_id, invalid_dummy_tx = vote_obj.validate_block(block)
    assert invalid_dummy_tx == [vote_obj.invalid_dummy_tx]


@pytest.mark.genesis
def test_validate_block_with_invalid_signature(b):
    from bigchaindb.pipelines import vote

    tx = dummy_tx(b)
    block = b.create_block([tx]).to_dict()
    block['signature'] = 'an invalid signature'

    vote_obj = vote.Vote()
    block_id, invalid_dummy_tx = vote_obj.validate_block(block)
    assert block_id == block['id']
    assert invalid_dummy_tx == [vote_obj.invalid_dummy_tx]


@pytest.mark.genesis
def test_vote_validate_transaction(b):
    from bigchaindb.pipelines import vote
    from bigchaindb.common.exceptions import ValidationError

    tx = dummy_tx(b)
    vote_obj = vote.Vote()
    validation = vote_obj.validate_tx(tx, 123, 1)
    assert validation == (True, 123, 1)

    with patch('bigchaindb.models.Transaction.validate') as validate:
        # Assert that validationerror gets caught
        validate.side_effect = ValidationError()
        validation = vote_obj.validate_tx(tx, 456, 10)
        assert validation == (False, 456, 10)

        # Assert that another error doesnt
        validate.side_effect = IOError()
        with pytest.raises(IOError):
            validation = vote_obj.validate_tx(tx, 456, 10)


@pytest.mark.genesis
def test_vote_accumulates_transactions(b):
    from bigchaindb.pipelines import vote

    vote_obj = vote.Vote()

    for _ in range(10):
        tx = dummy_tx(b)

    tx = tx
    validation = vote_obj.validate_tx(tx, 123, 1)
    assert validation == (True, 123, 1)

    tx.inputs[0].fulfillment.signature = None
    validation = vote_obj.validate_tx(tx, 456, 10)
    assert validation == (False, 456, 10)


@pytest.mark.bdb
def test_valid_block_voting_sequential(b, genesis_block, monkeypatch):
    from bigchaindb.backend import query
    from bigchaindb.common import crypto, utils
    from bigchaindb.pipelines import vote

    monkeypatch.setattr('time.time', lambda: 1111111111)
    vote_obj = vote.Vote()
    block = dummy_block(b)

    for tx, block_id, num_tx in vote_obj.ungroup(block.id, block.transactions):
        last_vote = vote_obj.vote(*vote_obj.validate_tx(tx, block_id, num_tx))

    vote_obj.write_vote(last_vote)
    vote_rs = query.get_votes_by_block_id_and_voter(b.connection, block_id, b.me)
    vote_doc = vote_rs.next()

    assert vote_doc['vote'] == {'voting_for_block': block.id,
                                'previous_block': genesis_block.id,
                                'is_block_valid': True,
                                'invalid_reason': None,
                                'timestamp': '1111111111'}

    serialized_vote = utils.serialize(vote_doc['vote']).encode()
    assert vote_doc['node_pubkey'] == b.me
    assert crypto.PublicKey(b.me).verify(serialized_vote,
                                         vote_doc['signature']) is True


@pytest.mark.bdb
def test_valid_block_voting_multiprocessing(b, genesis_block, monkeypatch):
    from bigchaindb.backend import query
    from bigchaindb.common import crypto, utils
    from bigchaindb.pipelines import vote

    inpipe = Pipe()
    outpipe = Pipe()

    monkeypatch.setattr('time.time', lambda: 1111111111)
    vote_pipeline = vote.create_pipeline()
    vote_pipeline.setup(indata=inpipe, outdata=outpipe)

    block = dummy_block(b)
    block_dict = decouple_assets(b, block)

    inpipe.put(block_dict)
    vote_pipeline.start()
    vote_out = outpipe.get()
    vote_pipeline.terminate()

    vote_rs = query.get_votes_by_block_id_and_voter(b.connection, block.id, b.me)
    vote_doc = vote_rs.next()
    assert vote_out['vote'] == vote_doc['vote']
    assert vote_doc['vote'] == {'voting_for_block': block.id,
                                'previous_block': genesis_block.id,
                                'is_block_valid': True,
                                'invalid_reason': None,
                                'timestamp': '1111111111'}

    serialized_vote = utils.serialize(vote_doc['vote']).encode()
    assert vote_doc['node_pubkey'] == b.me
    assert crypto.PublicKey(b.me).verify(serialized_vote,
                                         vote_doc['signature']) is True


@pytest.mark.bdb
def test_valid_block_voting_with_create_transaction(b,
                                                    genesis_block,
                                                    monkeypatch):
    from bigchaindb.backend import query
    from bigchaindb.common import crypto, utils
    from bigchaindb.models import Transaction
    from bigchaindb.pipelines import vote

    # create a `CREATE` transaction
    test_user_priv, test_user_pub = crypto.generate_key_pair()
    tx = Transaction.create([b.me], [([test_user_pub], 1)])
    tx = tx.sign([b.me_private])

    monkeypatch.setattr('time.time', lambda: 1111111111)
    block = b.create_block([tx])
    block_dict = decouple_assets(b, block)

    inpipe = Pipe()
    outpipe = Pipe()

    vote_pipeline = vote.create_pipeline()
    vote_pipeline.setup(indata=inpipe, outdata=outpipe)

    inpipe.put(block_dict)
    vote_pipeline.start()
    vote_out = outpipe.get()
    vote_pipeline.terminate()

    vote_rs = query.get_votes_by_block_id_and_voter(b.connection, block.id, b.me)
    vote_doc = vote_rs.next()
    assert vote_out['vote'] == vote_doc['vote']
    assert vote_doc['vote'] == {'voting_for_block': block.id,
                                'previous_block': genesis_block.id,
                                'is_block_valid': True,
                                'invalid_reason': None,
                                'timestamp': '1111111111'}

    serialized_vote = utils.serialize(vote_doc['vote']).encode()
    assert vote_doc['node_pubkey'] == b.me
    assert crypto.PublicKey(b.me).verify(serialized_vote,
                                         vote_doc['signature']) is True


@pytest.mark.bdb
def test_valid_block_voting_with_transfer_transactions(monkeypatch,
                                                       b, genesis_block):
    from bigchaindb.backend import query
    from bigchaindb.common import crypto, utils
    from bigchaindb.models import Transaction
    from bigchaindb.pipelines import vote

    # create a `CREATE` transaction
    test_user_priv, test_user_pub = crypto.generate_key_pair()
    tx = Transaction.create([b.me], [([test_user_pub], 1)])
    tx = tx.sign([b.me_private])

    monkeypatch.setattr('time.time', lambda: 1000000000)
    block = b.create_block([tx])
    b.write_block(block)

    # create a `TRANSFER` transaction
    test_user2_priv, test_user2_pub = crypto.generate_key_pair()
    tx2 = Transaction.transfer(tx.to_inputs(), [([test_user2_pub], 1)],
                               asset_id=tx.id)
    tx2 = tx2.sign([test_user_priv])

    monkeypatch.setattr('time.time', lambda: 2000000000)
    block2 = b.create_block([tx2])
    b.write_block(block2)

    inpipe = Pipe()
    outpipe = Pipe()

    vote_pipeline = vote.create_pipeline()
    vote_pipeline.setup(indata=inpipe, outdata=outpipe)

    vote_pipeline.start()
    inpipe.put(block.to_dict())
    time.sleep(1)
    inpipe.put(block2.to_dict())
    vote_out = outpipe.get()
    vote2_out = outpipe.get()
    vote_pipeline.terminate()

    vote_rs = query.get_votes_by_block_id_and_voter(b.connection, block.id, b.me)
    vote_doc = vote_rs.next()
    assert vote_out['vote'] == vote_doc['vote']
    assert vote_doc['vote'] == {'voting_for_block': block.id,
                                'previous_block': genesis_block.id,
                                'is_block_valid': True,
                                'invalid_reason': None,
                                'timestamp': '2000000000'}

    serialized_vote = utils.serialize(vote_doc['vote']).encode()
    assert vote_doc['node_pubkey'] == b.me
    assert crypto.PublicKey(b.me).verify(serialized_vote,
                                         vote_doc['signature']) is True

    vote2_rs = query.get_votes_by_block_id_and_voter(b.connection, block2.id, b.me)
    vote2_doc = vote2_rs.next()
    assert vote2_out['vote'] == vote2_doc['vote']
    assert vote2_doc['vote'] == {'voting_for_block': block2.id,
                                 'previous_block': block.id,
                                 'is_block_valid': True,
                                 'invalid_reason': None,
                                 'timestamp': '2000000000'}

    serialized_vote2 = utils.serialize(vote2_doc['vote']).encode()
    assert vote2_doc['node_pubkey'] == b.me
    assert crypto.PublicKey(b.me).verify(serialized_vote2,
                                         vote2_doc['signature']) is True


@pytest.mark.bdb
def test_unsigned_tx_in_block_voting(monkeypatch, b, user_pk, genesis_block):
    from bigchaindb.backend import query
    from bigchaindb.common import crypto, utils
    from bigchaindb.models import Transaction
    from bigchaindb.pipelines import vote

    inpipe = Pipe()
    outpipe = Pipe()

    monkeypatch.setattr('time.time', lambda: 1111111111)
    vote_pipeline = vote.create_pipeline()
    vote_pipeline.setup(indata=inpipe, outdata=outpipe)

    # NOTE: `tx` is invalid, because it wasn't signed.
    tx = Transaction.create([b.me], [([b.me], 1)])
    block = b.create_block([tx])

    inpipe.put(block.to_dict())
    vote_pipeline.start()
    vote_out = outpipe.get()
    vote_pipeline.terminate()

    vote_rs = query.get_votes_by_block_id_and_voter(b.connection, block.id, b.me)
    vote_doc = vote_rs.next()
    assert vote_out['vote'] == vote_doc['vote']
    assert vote_doc['vote'] == {'voting_for_block': block.id,
                                'previous_block': genesis_block.id,
                                'is_block_valid': False,
                                'invalid_reason': None,
                                'timestamp': '1111111111'}

    serialized_vote = utils.serialize(vote_doc['vote']).encode()
    assert vote_doc['node_pubkey'] == b.me
    assert crypto.PublicKey(b.me).verify(serialized_vote,
                                         vote_doc['signature']) is True


@pytest.mark.bdb
def test_invalid_id_tx_in_block_voting(monkeypatch, b, user_pk, genesis_block):
    from bigchaindb.backend import query
    from bigchaindb.common import crypto, utils
    from bigchaindb.models import Transaction
    from bigchaindb.pipelines import vote

    inpipe = Pipe()
    outpipe = Pipe()

    monkeypatch.setattr('time.time', lambda: 1111111111)
    vote_pipeline = vote.create_pipeline()
    vote_pipeline.setup(indata=inpipe, outdata=outpipe)

    # NOTE: `tx` is invalid, because its id is not corresponding to its content
    tx = Transaction.create([b.me], [([b.me], 1)])
    tx = tx.sign([b.me_private])
    block = b.create_block([tx]).to_dict()
    block['block']['transactions'][0]['id'] = 'an invalid tx id'

    inpipe.put(block)
    vote_pipeline.start()
    vote_out = outpipe.get()
    vote_pipeline.terminate()

    vote_rs = query.get_votes_by_block_id_and_voter(b.connection, block['id'], b.me)
    vote_doc = vote_rs.next()
    assert vote_out['vote'] == vote_doc['vote']
    assert vote_doc['vote'] == {'voting_for_block': block['id'],
                                'previous_block': genesis_block.id,
                                'is_block_valid': False,
                                'invalid_reason': None,
                                'timestamp': '1111111111'}

    serialized_vote = utils.serialize(vote_doc['vote']).encode()
    assert vote_doc['node_pubkey'] == b.me
    assert crypto.PublicKey(b.me).verify(serialized_vote,
                                         vote_doc['signature']) is True


@pytest.mark.bdb
def test_invalid_content_in_tx_in_block_voting(monkeypatch, b,
                                               user_pk, genesis_block):
    from bigchaindb.backend import query
    from bigchaindb.common import crypto, utils
    from bigchaindb.models import Transaction
    from bigchaindb.pipelines import vote

    inpipe = Pipe()
    outpipe = Pipe()

    monkeypatch.setattr('time.time', lambda: 1111111111)
    vote_pipeline = vote.create_pipeline()
    vote_pipeline.setup(indata=inpipe, outdata=outpipe)

    # NOTE: `tx` is invalid, because its content is not corresponding to its id
    tx = Transaction.create([b.me], [([b.me], 1)])
    tx = tx.sign([b.me_private])
    block = b.create_block([tx]).to_dict()
    block['block']['transactions'][0]['id'] = 'an invalid tx id'

    inpipe.put(block)
    vote_pipeline.start()
    vote_out = outpipe.get()
    vote_pipeline.terminate()

    vote_rs = query.get_votes_by_block_id_and_voter(b.connection, block['id'], b.me)
    vote_doc = vote_rs.next()
    assert vote_out['vote'] == vote_doc['vote']
    assert vote_doc['vote'] == {'voting_for_block': block['id'],
                                'previous_block': genesis_block.id,
                                'is_block_valid': False,
                                'invalid_reason': None,
                                'timestamp': '1111111111'}

    serialized_vote = utils.serialize(vote_doc['vote']).encode()
    assert vote_doc['node_pubkey'] == b.me
    assert crypto.PublicKey(b.me).verify(serialized_vote,
                                         vote_doc['signature']) is True


@pytest.mark.bdb
def test_invalid_block_voting(monkeypatch, b, user_pk, genesis_block):
    from bigchaindb.backend import query
    from bigchaindb.common import crypto, utils
    from bigchaindb.pipelines import vote

    inpipe = Pipe()
    outpipe = Pipe()

    monkeypatch.setattr('time.time', lambda: 1111111111)
    vote_pipeline = vote.create_pipeline()
    vote_pipeline.setup(indata=inpipe, outdata=outpipe)

    block = dummy_block(b).to_dict()
    block['block']['id'] = 'this-is-not-a-valid-hash'

    inpipe.put(block)
    vote_pipeline.start()
    vote_out = outpipe.get()
    vote_pipeline.terminate()

    vote_rs = query.get_votes_by_block_id_and_voter(b.connection, block['id'], b.me)
    vote_doc = vote_rs.next()
    assert vote_out['vote'] == vote_doc['vote']
    assert vote_doc['vote'] == {'voting_for_block': block['id'],
                                'previous_block': genesis_block.id,
                                'is_block_valid': False,
                                'invalid_reason': None,
                                'timestamp': '1111111111'}

    serialized_vote = utils.serialize(vote_doc['vote']).encode()
    assert vote_doc['node_pubkey'] == b.me
    assert crypto.PublicKey(b.me).verify(serialized_vote,
                                         vote_doc['signature']) is True


@pytest.mark.genesis
def test_voter_checks_for_previous_vote(monkeypatch, b):
    from bigchaindb.backend import query
    from bigchaindb.pipelines import vote

    inpipe = Pipe()
    outpipe = Pipe()

    monkeypatch.setattr('time.time', lambda: 1000000000)

    monkeypatch.setattr('time.time', lambda: 1000000020)
    block_1 = dummy_block(b)
    inpipe.put(block_1.to_dict())
    assert len(list(query.get_votes_by_block_id(b.connection, block_1.id))) == 0

    vote_pipeline = vote.create_pipeline()
    vote_pipeline.setup(indata=inpipe, outdata=outpipe)
    vote_pipeline.start()

    # wait for the result
    outpipe.get()

    # queue block for voting AGAIN
    monkeypatch.setattr('time.time', lambda: 1000000030)
    inpipe.put(block_1.to_dict())

    # queue another block
    monkeypatch.setattr('time.time', lambda: 1000000040)
    block_2 = dummy_block(b)
    inpipe.put(block_2.to_dict())

    # wait for the result of the new block
    outpipe.get()

    vote_pipeline.terminate()

    assert len(list(query.get_votes_by_block_id(b.connection, block_1.id))) == 1
    assert len(list(query.get_votes_by_block_id(b.connection, block_2.id))) == 1


@patch.object(Pipeline, 'start')
@pytest.mark.genesis
def test_start(mock_start, b):
    # TODO: `block.start` is just a wrapper around `vote.create_pipeline`,
    #       that is tested by `test_full_pipeline`.
    #       If anyone has better ideas on how to test this, please do a PR :)
    from bigchaindb.pipelines import vote
    vote.start()
    mock_start.assert_called_with()


@pytest.mark.genesis
def test_vote_no_double_inclusion(b):
    from bigchaindb.pipelines import vote

    tx = dummy_tx(b)
    block = b.create_block([tx])
    r = vote.Vote().validate_tx(tx, block.id, 1)
    assert r == (True, block.id, 1)

    b.write_block(block)
    r = vote.Vote().validate_tx(tx, 'other_block_id', 1)
    assert r == (False, 'other_block_id', 1)


@pytest.mark.genesis
def test_vote_changefeed(b):
    from bigchaindb.pipelines import vote
    from multiprocessing import Queue

    changefeed = vote.get_changefeed()
    changefeed.outqueue = Queue()
    changefeed.start()
    tx = dummy_tx(b)
    block = b.create_block([tx])
    b.write_block(block)
    assert changefeed.outqueue.get() == block.decouple_assets()[1]
    changefeed.terminate()
