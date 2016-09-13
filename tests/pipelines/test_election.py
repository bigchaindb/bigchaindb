import time
import random
from bigchaindb import crypto, Bigchain
from unittest.mock import patch

import rethinkdb as r

from bigchaindb.pipelines import election
from multipipes import Pipe, Pipeline


def test_check_for_quorum_invalid(b, user_vk):
    e = election.Election()

    # create blocks with transactions
    tx1 = b.create_transaction(b.me, user_vk, None, 'CREATE')
    test_block = b.create_block([tx1])

    # simulate a federation with four voters
    key_pairs = [crypto.generate_key_pair() for _ in range(4)]
    test_federation = [Bigchain(public_key=key_pair[1], private_key=key_pair[0])
                       for key_pair in key_pairs]

    # add voters to block and write
    test_block['block']['voters'] = [key_pair[1] for key_pair in key_pairs]
    b.write_block(test_block)

    # split_vote (invalid)
    votes = [member.vote(test_block['id'], 'abc', True) for member in test_federation[:2]] + \
                   [member.vote(test_block['id'], 'abc', False) for member in test_federation[2:]]

    # cast votes
    r.table('votes').insert(votes, durability='hard').run(b.conn)

    # since this block is now invalid, should pass to the next process
    assert e.check_for_quorum(votes[-1]) == test_block


def test_check_for_quorum_invalid_prev_node(b, user_vk):
    e = election.Election()

    # create blocks with transactions
    tx1 = b.create_transaction(b.me, user_vk, None, 'CREATE')
    test_block = b.create_block([tx1])

    # simulate a federation with four voters
    key_pairs = [crypto.generate_key_pair() for _ in range(4)]
    test_federation = [Bigchain(public_key=key_pair[1], private_key=key_pair[0])
                       for key_pair in key_pairs]

    # add voters to block and write
    test_block['block']['voters'] = [key_pair[1] for key_pair in key_pairs]
    b.write_block(test_block)

    # split vote over prev node
    votes = [member.vote(test_block['id'], 'abc', True) for member in test_federation[:2]] + \
                   [member.vote(test_block['id'], 'def', True) for member in test_federation[2:]]

    # cast votes
    r.table('votes').insert(votes, durability='hard').run(b.conn)

    # since nodes cannot agree on prev block, the block is invalid
    assert e.check_for_quorum(votes[-1]) == test_block


def test_check_for_quorum_valid(b, user_vk):
    e = election.Election()

    # create blocks with transactions
    tx1 = b.create_transaction(b.me, user_vk, None, 'CREATE')
    test_block = b.create_block([tx1])

    # simulate a federation with four voters
    key_pairs = [crypto.generate_key_pair() for _ in range(4)]
    test_federation = [Bigchain(public_key=key_pair[1], private_key=key_pair[0])
                       for key_pair in key_pairs]

    # add voters to block and write
    test_block['block']['voters'] = [key_pair[1] for key_pair in key_pairs]
    b.write_block(test_block)

    # votes for block one
    votes = [member.vote(test_block['id'], 'abc', True)
                  for member in test_federation]
    # cast votes
    r.table('votes').insert(votes, durability='hard').run(b.conn)

    # since this block is valid, should go nowhere
    assert e.check_for_quorum(votes[-1]) is None


def test_check_requeue_transaction(b, user_vk):
    e = election.Election()

    # create blocks with transactions
    tx1 = b.create_transaction(b.me, user_vk, None, 'CREATE')
    test_block = b.create_block([tx1])

    e.requeue_transactions(test_block)
    tx_backlog = r.table('backlog').get(tx1['id']).run(b.conn)
    tx_backlog.pop('assignee')
    tx_backlog.pop('assignment_timestamp')

    assert tx_backlog == tx1


@patch.object(Pipeline, 'start')
def test_start(mock_start):
    # TODO: `block.election` is just a wrapper around `block.create_pipeline`,
    #       that is tested by `test_full_pipeline`.
    #       If anyone has better ideas on how to test this, please do a PR :)
    election.start()
    mock_start.assert_called_with()


def test_full_pipeline(b, user_vk):
    outpipe = Pipe()

    # write two blocks
    txs = []
    for i in range(100):
        tx = b.create_transaction(b.me, user_vk, None, 'CREATE')
        tx = b.sign_transaction(tx, b.me_private)
        txs.append(tx)

    valid_block = b.create_block(txs)
    b.write_block(valid_block)

    txs = []
    for i in range(100):
        tx = b.create_transaction(b.me, user_vk, None, 'CREATE')
        tx = b.sign_transaction(tx, b.me_private)
        txs.append(tx)

    invalid_block = b.create_block(txs)
    b.write_block(invalid_block)

    pipeline = election.create_pipeline()
    pipeline.setup(indata=election.get_changefeed(), outdata=outpipe)
    pipeline.start()
    time.sleep(1)
    # vote one block valid, one invalid
    vote_valid = b.vote(valid_block['id'], 'abc', True)
    vote_invalid = b.vote(invalid_block['id'], 'abc', False)

    r.table('votes').insert(vote_valid, durability='hard').run(b.conn)
    r.table('votes').insert(vote_invalid, durability='hard').run(b.conn)

    outpipe.get()
    pipeline.terminate()

    # only transactions from the invalid block should be returned to
    # the backlog
    assert r.table('backlog').count().run(b.conn) == 100
    tx_from_block = set([tx['id'] for tx in invalid_block['block']['transactions']])
    tx_from_backlog = set([tx['id'] for tx in list(r.table('backlog').run(b.conn))])
    assert tx_from_block == tx_from_backlog
