import pytest
import time
import rethinkdb as r
import multiprocessing as mp

from bigchaindb import util

from bigchaindb.voter import Voter, Election, BlockStream
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


class TestBigchainVoter(object):

    def test_vote_creation_valid(self, b):
        # create valid block
        block = dummy_block()
        # retrieve vote
        vote = b.vote(block['id'], 'abc', True)

        # assert vote is correct
        assert vote['vote']['voting_for_block'] == block['id']
        assert vote['vote']['previous_block'] == 'abc'
        assert vote['vote']['is_block_valid'] is True
        assert vote['vote']['invalid_reason'] is None
        assert vote['node_pubkey'] == b.me
        assert crypto.VerifyingKey(b.me).verify(util.serialize(vote['vote']), vote['signature']) is True

    def test_vote_creation_invalid(self, b):
        # create valid block
        block = dummy_block()
        # retrieve vote
        vote = b.vote(block['id'], 'abc', False)

        # assert vote is correct
        assert vote['vote']['voting_for_block'] == block['id']
        assert vote['vote']['previous_block'] == 'abc'
        assert vote['vote']['is_block_valid'] is False
        assert vote['vote']['invalid_reason'] is None
        assert vote['node_pubkey'] == b.me
        assert crypto.VerifyingKey(b.me).verify(util.serialize(vote['vote']), vote['signature']) is True

    def test_voter_considers_unvoted_blocks_when_single_node(self, b):
        # simulate a voter going donw in a single node environment
        b.create_genesis_block()

        # insert blocks in the database while the voter process is not listening
        # (these blocks won't appear in the changefeed)
        block_1 = dummy_block()
        b.write_block(block_1, durability='hard')
        block_2 = dummy_block()
        b.write_block(block_2, durability='hard')

        # voter is back online, we simulate that by creating a queue and a Voter instance
        q_new_block = mp.Queue()
        voter = Voter(q_new_block)

        # vote
        voter.start()
        time.sleep(1)

        # create a new block that will appear in the changefeed
        block_3 = dummy_block()
        b.write_block(block_3, durability='hard')

        time.sleep(1)
        voter.kill()

        # retrive blocks from bigchain
        blocks = list(r.table('bigchain')
                       .order_by(r.asc((r.row['block']['timestamp'])))
                       .run(b.conn))

        # FIXME: remove genesis block, we don't vote on it (might change in the future)
        blocks.pop(0)

        # retrieve vote
        votes = r.table('votes').run(b.conn)
        votes = list(votes)

        assert all(vote['node_pubkey'] == b.me for vote in votes)

    def test_voter_chains_blocks_with_the_previous_ones(self, b):
        b.create_genesis_block()
        # sleep so that `block_*` as a higher timestamp then `genesis`
        time.sleep(1)
        block_1 = dummy_block()
        b.write_block(block_1, durability='hard')
        time.sleep(1)
        block_2 = dummy_block()
        b.write_block(block_2, durability='hard')

        q_new_block = mp.Queue()

        voter = Voter(q_new_block)
        voter.start()
        time.sleep(1)
        voter.kill()

        # retrive blocks from bigchain
        blocks = list(r.table('bigchain')
                       .order_by(r.asc((r.row['block']['timestamp'])))
                       .run(b.conn))

        # retrieve votes
        votes = list(r.table('votes').run(b.conn))

        assert votes[0]['vote']['voting_for_block'] in (blocks[1]['id'], blocks[2]['id'])
        assert votes[1]['vote']['voting_for_block'] in (blocks[1]['id'], blocks[2]['id'])

    def test_voter_checks_for_previous_vote(self, b):
        b.create_genesis_block()
        block_1 = dummy_block()
        b.write_block(block_1, durability='hard')

        q_new_block = mp.Queue()

        voter = Voter(q_new_block)
        voter.start()

        time.sleep(1)
        retrieved_block = r.table('bigchain').get(block_1['id']).run(b.conn)

        # queue block for voting AGAIN
        q_new_block.put(retrieved_block)
        time.sleep(1)
        voter.kill()

        re_retrieved_block = r.table('bigchain').get(block_1['id']).run(b.conn)

        # block should be unchanged
        assert retrieved_block == re_retrieved_block

    @pytest.mark.skipif(reason='Updating the block_number must be atomic')
    def test_updating_block_number_must_be_atomic(self):
        pass


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


class TestBlockStream(object):

    def test_if_federation_size_is_greater_than_one_ignore_past_blocks(self, b):
        for _ in range(5):
            b.nodes_except_me.append(crypto.generate_key_pair()[1])
        new_blocks = mp.Queue()
        bs = BlockStream(new_blocks)
        block_1 = dummy_block()
        new_blocks.put(block_1)
        assert block_1 == bs.get()

    def test_if_no_old_blocks_get_should_return_new_blocks(self, b):
        new_blocks = mp.Queue()
        bs = BlockStream(new_blocks)

        # create two blocks
        block_1 = dummy_block()
        block_2 = dummy_block()

        # write the blocks
        b.write_block(block_1, durability='hard')
        b.write_block(block_2, durability='hard')

        # simulate a changefeed
        new_blocks.put(block_1)
        new_blocks.put(block_2)

        # and check if we get exactly these two blocks
        assert bs.get() == block_1
        assert bs.get() == block_2

    @pytest.mark.skipif(reason='We may have duplicated blocks when retrieving the BlockStream')
    def test_ignore_duplicated_blocks_when_retrieving_the_blockstream(self):
        pass
