import time
from unittest.mock import patch

from bigchaindb.common import crypto
import rethinkdb as r
from multipipes import Pipe, Pipeline

from bigchaindb import Bigchain
from bigchaindb.pipelines import election


def test_check_for_quorum_invalid(b, user_vk):
    from bigchaindb.models import Transaction

    e = election.Election()

    # create blocks with transactions
    tx1 = Transaction.create([b.me], [user_vk])
    test_block = b.create_block([tx1])

    # simulate a federation with four voters
    key_pairs = [crypto.generate_key_pair() for _ in range(4)]
    test_federation = [Bigchain(public_key=key_pair[1], private_key=key_pair[0])
                       for key_pair in key_pairs]

    # add voters to block and write
    test_block.voters = [key_pair[1] for key_pair in key_pairs]
    test_block = test_block.sign(b.me_private)
    b.write_block(test_block)

    # split_vote (invalid)
    votes = [member.vote(test_block.id, 'abc', True) for member in test_federation[:2]] + \
                   [member.vote(test_block.id, 'abc', False) for member in test_federation[2:]]

    # cast votes
    b.connection.run(r.table('votes').insert(votes, durability='hard'))

    # since this block is now invalid, should pass to the next process
    assert e.check_for_quorum(votes[-1]) == test_block


def test_check_for_quorum_invalid_prev_node(b, user_vk):
    from bigchaindb.models import Transaction
    e = election.Election()

    # create blocks with transactions
    tx1 = Transaction.create([b.me], [user_vk])
    test_block = b.create_block([tx1])

    # simulate a federation with four voters
    key_pairs = [crypto.generate_key_pair() for _ in range(4)]
    test_federation = [Bigchain(public_key=key_pair[1], private_key=key_pair[0])
                       for key_pair in key_pairs]

    # add voters to block and write
    test_block.voters = [key_pair[1] for key_pair in key_pairs]
    test_block = test_block.sign(b.me_private)
    b.write_block(test_block)

    # split vote over prev node
    votes = [member.vote(test_block.id, 'abc', True) for member in test_federation[:2]] + \
                   [member.vote(test_block.id, 'def', True) for member in test_federation[2:]]

    # cast votes
    b.connection.run(r.table('votes').insert(votes, durability='hard'))

    # since nodes cannot agree on prev block, the block is invalid
    assert e.check_for_quorum(votes[-1]) == test_block


def test_check_for_quorum_valid(b, user_vk):
    from bigchaindb.models import Transaction

    e = election.Election()

    # create blocks with transactions
    tx1 = Transaction.create([b.me], [user_vk])
    test_block = b.create_block([tx1])

    # simulate a federation with four voters
    key_pairs = [crypto.generate_key_pair() for _ in range(4)]
    test_federation = [Bigchain(public_key=key_pair[1], private_key=key_pair[0])
                       for key_pair in key_pairs]

    # add voters to block and write
    test_block.voters = [key_pair[1] for key_pair in key_pairs]
    test_block = test_block.sign(b.me_private)
    b.write_block(test_block)

    # votes for block one
    votes = [member.vote(test_block.id, 'abc', True)
             for member in test_federation]
    # cast votes
    b.connection.run(r.table('votes').insert(votes, durability='hard'))

    # since this block is valid, should go nowhere
    assert e.check_for_quorum(votes[-1]) is None


def test_check_requeue_transaction(b, user_vk):
    from bigchaindb.models import Transaction

    e = election.Election()

    # create blocks with transactions
    tx1 = Transaction.create([b.me], [user_vk])
    test_block = b.create_block([tx1])

    e.requeue_transactions(test_block)
    backlog_tx = b.connection.run(r.table('backlog').get(tx1.id))
    backlog_tx.pop('assignee')
    backlog_tx.pop('assignment_timestamp')
    assert backlog_tx == tx1.to_dict()


@patch.object(Pipeline, 'start')
def test_start(mock_start):
    # TODO: `block.election` is just a wrapper around `block.create_pipeline`,
    #       that is tested by `test_full_pipeline`.
    #       If anyone has better ideas on how to test this, please do a PR :)
    election.start()
    mock_start.assert_called_with()


def test_full_pipeline(b, user_vk):
    import random
    from bigchaindb.models import Transaction

    outpipe = Pipe()

    # write two blocks
    txs = []
    for i in range(100):
        tx = Transaction.create([b.me], [user_vk], {'msg': random.random()})
        tx = tx.sign([b.me_private])
        txs.append(tx)

    valid_block = b.create_block(txs)
    b.write_block(valid_block)

    txs = []
    for i in range(100):
        tx = Transaction.create([b.me], [user_vk], {'msg': random.random()})
        tx = tx.sign([b.me_private])
        txs.append(tx)

    invalid_block = b.create_block(txs)
    b.write_block(invalid_block)

    pipeline = election.create_pipeline()
    pipeline.setup(indata=election.get_changefeed(), outdata=outpipe)
    pipeline.start()
    time.sleep(1)
    # vote one block valid, one invalid
    vote_valid = b.vote(valid_block.id, 'abc', True)
    vote_invalid = b.vote(invalid_block.id, 'abc', False)

    b.connection.run(r.table('votes').insert(vote_valid, durability='hard'))
    b.connection.run(r.table('votes').insert(vote_invalid, durability='hard'))

    outpipe.get()
    pipeline.terminate()

    # only transactions from the invalid block should be returned to
    # the backlog
    assert b.connection.run(r.table('backlog').count()) == 100
    # NOTE: I'm still, I'm still tx from the block.
    tx_from_block = set([tx.id for tx in invalid_block.transactions])
    tx_from_backlog = set([tx['id'] for tx in list(b.connection.run(r.table('backlog')))])
    assert tx_from_block == tx_from_backlog
