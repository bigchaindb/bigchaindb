import time
import rethinkdb as r
import multiprocessing as mp

from bigchaindb.voter import Election
from bigchaindb import crypto, Bigchain


# Some util functions
def dummy_tx():
    b = Bigchain()
    tx = b.create_transaction(b.me, b.me, None, 'CREATE')
    tx_signed = b.sign_transaction(tx, b.me_private)
    return tx_signed


def dummy_block():
    b = Bigchain()
    block = b.create_block([dummy_tx()])
    return block


class TestBlockElection(object):

    def test_quorum(self, b):
        # create a new block
        test_block = dummy_block()

        # simulate a federation with four voters
        key_pairs = [crypto.generate_key_pair() for _ in range(4)]
        test_federation = [Bigchain(public_key=key_pair[1], private_key=key_pair[0])
                           for key_pair in key_pairs]

        # dummy block with test federation public keys as voters
        test_block['block']['voters'] = [key_pair[1] for key_pair in key_pairs]

        # fake "yes" votes
        valid_vote = [member.vote(test_block['id'], 'abc', True)
                      for member in test_federation]

        # fake "no" votes
        invalid_vote = [member.vote(test_block['id'], 'abc', False)
                        for member in test_federation]

        # fake "yes" votes with incorrect signatures
        improperly_signed_valid_vote = [member.vote(test_block['id'], 'abc', True) for
                                        member in test_federation]
        [vote['vote'].update(this_should_ruin_things='lol')
         for vote in improperly_signed_valid_vote]

        # test unanimously valid block
        r.table('votes').insert(valid_vote, durability='hard').run(b.conn)
        assert b.block_election_status(test_block) == Bigchain.BLOCK_VALID
        r.table('votes').delete().run(b.conn)

        # test partial quorum situations
        r.table('votes').insert(valid_vote[:2], durability='hard').run(b.conn)
        assert b.block_election_status(test_block) == Bigchain.BLOCK_UNDECIDED
        r.table('votes').delete().run(b.conn)
        #
        r.table('votes').insert(valid_vote[:3], durability='hard').run(b.conn)
        assert b.block_election_status(test_block) == Bigchain.BLOCK_VALID
        r.table('votes').delete().run(b.conn)
        #
        r.table('votes').insert(invalid_vote[:2], durability='hard').run(b.conn)
        assert b.block_election_status(test_block) == Bigchain.BLOCK_INVALID
        r.table('votes').delete().run(b.conn)

        # test unanimously valid block with one improperly signed vote -- should still succeed
        r.table('votes').insert(valid_vote[:3] + improperly_signed_valid_vote[3:], durability='hard').run(b.conn)
        assert b.block_election_status(test_block) == Bigchain.BLOCK_VALID
        r.table('votes').delete().run(b.conn)

        # test unanimously valid block with two improperly signed votes -- should fail
        r.table('votes').insert(valid_vote[:2] + improperly_signed_valid_vote[2:], durability='hard').run(b.conn)
        assert b.block_election_status(test_block) == Bigchain.BLOCK_INVALID
        r.table('votes').delete().run(b.conn)

        # test block with minority invalid vote
        r.table('votes').insert(invalid_vote[:1] + valid_vote[1:], durability='hard').run(b.conn)
        assert b.block_election_status(test_block) == Bigchain.BLOCK_VALID
        r.table('votes').delete().run(b.conn)

        # test split vote
        r.table('votes').insert(invalid_vote[:2] + valid_vote[2:], durability='hard').run(b.conn)
        assert b.block_election_status(test_block) == Bigchain.BLOCK_INVALID
        r.table('votes').delete().run(b.conn)

        # test undecided
        r.table('votes').insert(valid_vote[:2], durability='hard').run(b.conn)
        assert b.block_election_status(test_block) == Bigchain.BLOCK_UNDECIDED
        r.table('votes').delete().run(b.conn)

        # change signatures in block, should fail
        test_block['block']['voters'][0] = 'abc'
        test_block['block']['voters'][1] = 'abc'
        r.table('votes').insert(valid_vote, durability='hard').run(b.conn)
        assert b.block_election_status(test_block) == Bigchain.BLOCK_INVALID

    def test_quorum_odd(self, b):
        # test partial quorum situations for odd numbers of voters
        # create a new block
        test_block = dummy_block()

        # simulate a federation with four voters
        key_pairs = [crypto.generate_key_pair() for _ in range(5)]
        test_federation = [Bigchain(public_key=key_pair[1], private_key=key_pair[0])
                           for key_pair in key_pairs]

        # dummy block with test federation public keys as voters
        test_block['block']['voters'] = [key_pair[1] for key_pair in key_pairs]

        # fake "yes" votes
        valid_vote = [member.vote(test_block['id'], 'abc', True)
                      for member in test_federation]

        # fake "no" votes
        invalid_vote = [member.vote(test_block['id'], 'abc', False)
                        for member in test_federation]

        r.table('votes').insert(valid_vote[:2], durability='hard').run(b.conn)
        assert b.block_election_status(test_block) == Bigchain.BLOCK_UNDECIDED
        r.table('votes').delete().run(b.conn)

        r.table('votes').insert(invalid_vote[:2], durability='hard').run(b.conn)
        assert b.block_election_status(test_block) == Bigchain.BLOCK_UNDECIDED
        r.table('votes').delete().run(b.conn)

        r.table('votes').insert(valid_vote[:3], durability='hard').run(b.conn)
        assert b.block_election_status(test_block) == Bigchain.BLOCK_VALID
        r.table('votes').delete().run(b.conn)

        r.table('votes').insert(invalid_vote[:3], durability='hard').run(b.conn)
        assert b.block_election_status(test_block) == Bigchain.BLOCK_INVALID
        r.table('votes').delete().run(b.conn)

    def test_tx_rewritten_after_invalid(self, b, user_vk):
        q_block_new_vote = mp.Queue()

        # create blocks with transactions
        tx1 = b.create_transaction(b.me, user_vk, None, 'CREATE')
        tx2 = b.create_transaction(b.me, user_vk, None, 'CREATE')
        test_block_1 = b.create_block([tx1])
        test_block_2 = b.create_block([tx2])

        # simulate a federation with four voters
        key_pairs = [crypto.generate_key_pair() for _ in range(4)]
        test_federation = [Bigchain(public_key=key_pair[1], private_key=key_pair[0])
                           for key_pair in key_pairs]

        # simulate a federation with four voters
        test_block_1['block']['voters'] = [key_pair[1] for key_pair in key_pairs]
        test_block_2['block']['voters'] = [key_pair[1] for key_pair in key_pairs]

        # votes for block one
        vote_1 = [member.vote(test_block_1['id'], 'abc', True)
                      for member in test_federation]

        # votes for block two
        vote_2 = [member.vote(test_block_2['id'], 'abc', True) for member in test_federation[:2]] + \
                       [member.vote(test_block_2['id'], 'abc', False) for member in test_federation[2:]]

        # construct valid block
        r.table('votes').insert(vote_1, durability='hard').run(b.conn)
        q_block_new_vote.put(test_block_1)

        # construct invalid block
        r.table('votes').insert(vote_2, durability='hard').run(b.conn)
        q_block_new_vote.put(test_block_2)

        election = Election(q_block_new_vote)
        election.start()
        time.sleep(1)
        election.kill()

        # tx1 was in a valid block, and should not be in the backlog
        assert r.table('backlog').get(tx1['id']).run(b.conn) is None

        # tx2 was in an invalid block and SHOULD be in the backlog
        assert r.table('backlog').get(tx2['id']).run(b.conn)['id'] == tx2['id']

