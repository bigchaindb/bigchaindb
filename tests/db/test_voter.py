import pytest
import time
import rethinkdb as r
import multiprocessing as mp

from bigchaindb import Bigchain
from bigchaindb.voter import Voter, BlockStream
from bigchaindb.crypto import PublicKey

from .conftest import USER_PUBLIC_KEY


class TestBigchainVoter(object):

    def test_valid_block_voting(self, b):
        q_new_block = mp.Queue()

        genesis = b.create_genesis_block()

        # create valid block
        block = b.create_block([])
        # assert block is valid
        assert b.is_valid_block(block)
        b.write_block(block, durability='hard')

        # create queue and voter
        voter = Voter(q_new_block)

        # vote
        voter.start()
        # wait for vote to be written
        time.sleep(1)
        voter.kill()

        # retrive block from bigchain
        blocks = list(r.table('bigchain')
                       .order_by(r.asc((r.row['block']['timestamp'])))
                       .run(b.conn))


        # validate vote
        assert len(blocks[1]['votes']) == 1
        vote = blocks[1]['votes'][0]

        assert vote['vote']['voting_for_block'] == block['id']
        assert vote['vote']['previous_block'] == genesis['id']
        assert vote['vote']['is_block_valid'] == True
        assert vote['vote']['invalid_reason'] == None
        assert vote['node_pubkey'] == b.me
        assert PublicKey(b.me).verify(b.serialize(vote['vote']), vote['signature']) == True


    def test_invalid_block_voting(self, b):
        # create queue and voter
        q_new_block = mp.Queue()
        voter = Voter(q_new_block)

        # create transaction
        transaction = b.create_transaction(b.me, USER_PUBLIC_KEY, None, 'CREATE')
        transaction_signed = b.sign_transaction(transaction, b.me_private)

        genesis = b.create_genesis_block()

        # create invalid block
        block = b.create_block([transaction_signed])
        # change transaction id to make it invalid
        block['block']['transactions'][0]['id'] = 'abc'
        assert not b.is_valid_block(block)
        b.write_block(block, durability='hard')


        # vote
        voter.start()
        time.sleep(1)
        voter.kill()

        # retrive block from bigchain
        blocks = list(r.table('bigchain')
                       .order_by(r.asc((r.row['block']['timestamp'])))
                       .run(b.conn))

        # validate vote
        assert len(blocks[1]['votes']) == 1
        vote = blocks[1]['votes'][0]

        assert vote['vote']['voting_for_block'] == block['id']
        assert vote['vote']['previous_block'] == genesis['id']
        assert vote['vote']['is_block_valid'] == False
        assert vote['vote']['invalid_reason'] == None
        assert vote['node_pubkey'] == b.me
        assert PublicKey(b.me).verify(b.serialize(vote['vote']), vote['signature']) == True

    def test_vote_creation_valid(self, b):
        # create valid block
        block = b.create_block([])
        # retrieve vote
        vote = b.vote(block, 'abc', True)

        # assert vote is correct
        assert vote['vote']['voting_for_block'] == block['id']
        assert vote['vote']['previous_block'] == 'abc'
        assert vote['vote']['is_block_valid'] == True
        assert vote['vote']['invalid_reason'] == None
        assert vote['node_pubkey'] == b.me
        assert PublicKey(b.me).verify(b.serialize(vote['vote']), vote['signature']) == True

    def test_vote_creation_invalid(self, b):
        # create valid block
        block = b.create_block([])
        # retrieve vote
        vote = b.vote(block, 'abc', False)

        # assert vote is correct
        assert vote['vote']['voting_for_block'] == block['id']
        assert vote['vote']['previous_block'] == 'abc'
        assert vote['vote']['is_block_valid'] == False
        assert vote['vote']['invalid_reason'] == None
        assert vote['node_pubkey'] == b.me
        assert PublicKey(b.me).verify(b.serialize(vote['vote']), vote['signature']) == True

    def test_voter_considers_unvoted_blocks_when_single_node(self, b):
        # simulate a voter going donw in a single node environment
        b.create_genesis_block()

        # insert blocks in the database while the voter process is not listening
        # (these blocks won't appear in the changefeed)
        block_1 = b.create_block([])
        b.write_block(block_1, durability='hard')
        block_2 = b.create_block([])
        b.write_block(block_2, durability='hard')

        # voter is back online, we simulate that by creating a queue and a Voter instance
        q_new_block = mp.Queue()
        voter = Voter(q_new_block)

        # create a new block that will appear in the changefeed
        block_3 = b.create_block([])
        b.write_block(block_3, durability='hard')

        # put the last block in the queue
        q_new_block.put(block_3)

        # vote
        voter.start()
        time.sleep(1)
        voter.kill()

        # retrive blocks from bigchain
        blocks = list(r.table('bigchain')
                       .order_by(r.asc((r.row['block']['timestamp'])))
                       .run(b.conn))

        # FIXME: remove genesis block, we don't vote on it (might change in the future)
        blocks.pop(0)

        assert all(block['votes'][0]['node_pubkey'] == b.me for block in blocks)

    def test_voter_chains_blocks_with_the_previous_ones(self, b):
        b.create_genesis_block()
        block_1 = b.create_block([])
        b.write_block(block_1, durability='hard')
        block_2 = b.create_block([])
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

        assert blocks[0]['block_number'] == 0
        assert blocks[1]['block_number'] == 1
        assert blocks[2]['block_number'] == 2

        # we don't vote on the genesis block right now
        # assert blocks[0]['votes'][0]['vote']['voting_for_block'] == genesis['id']
        assert blocks[1]['votes'][0]['vote']['voting_for_block'] == block_1['id']
        assert blocks[2]['votes'][0]['vote']['voting_for_block'] == block_2['id']

    @pytest.mark.skipif(reason='Updating the block_number must be atomic')
    def test_updating_block_number_must_be_atomic(self):
        pass



class TestBlockStream(object):

    def test_if_federation_size_is_greater_than_one_ignore_past_blocks(self, b):
        for _ in range(5):
            b.federation_nodes.append(b.generate_keys()[1])
        new_blocks = mp.Queue()
        bs = BlockStream(new_blocks)
        block_1 = b.create_block([])
        new_blocks.put(block_1)
        assert block_1 == bs.get()

    def test_if_no_old_blocks_get_should_return_new_blocks(self, b):
        new_blocks = mp.Queue()
        bs = BlockStream(new_blocks)

        # create two blocks
        block_1 = b.create_block([])
        block_2 = b.create_block([])

        # write the blocks
        b.write_block(block_1, durability='hard')
        b.write_block(block_2, durability='hard')

        # simulate a changefeed
        new_blocks.put(block_1)
        new_blocks.put(block_2)

        # and check if we get exactly these two blocks
        assert bs.get() == block_1
        assert bs.get() == block_2


    def test_if_old_blocks_get_should_return_old_block_first(self, b):
        # create two blocks
        block_1 = b.create_block([])
        block_2 = b.create_block([])

        # write the blocks
        b.write_block(block_1, durability='hard')
        b.write_block(block_2, durability='hard')

        new_blocks = mp.Queue()
        bs = BlockStream(new_blocks)

        # assert len(list(bs.old_blocks)) == 2
        # import pdb; pdb.set_trace()
        # from pprint import pprint as pp
        # pp(bs.old_blocks)
        # pp(block_1)
        # pp(block_2)

        # create two new blocks that will appear in the changefeed
        block_3 = b.create_block([])
        block_4 = b.create_block([])

        # simulate a changefeed
        new_blocks.put(block_3)
        new_blocks.put(block_4)

        assert len(bs.unvoted_blocks) == 2

        # and check if we get the old blocks first
        assert bs.get() == block_1
        assert bs.get() == block_2
        assert bs.get() == block_3
        assert bs.get() == block_4

    @pytest.mark.skipif(reason='We may have duplicated blocks when retrieving the BlockStream')
    def test_ignore_duplicated_blocks_when_retrieving_the_blockstream(self):
        pass
