import copy
import multiprocessing as mp
import random
import time
import json

import pytest
import rethinkdb as r
import cryptoconditions as cc

import bigchaindb
from bigchaindb import util
from bigchaindb import exceptions
from bigchaindb import crypto
from bigchaindb.voter import Voter
from bigchaindb.block import Block


@pytest.mark.skipif(reason='Some tests throw a ResourceWarning that might result in some weird '
                           'exceptions while running the tests. The problem seems to *not* '
                           'interfere with the correctness of the tests. ')
def test_remove_unclosed_sockets():
    pass


class TestBigchainApi(object):
    def test_create_transaction_create(self, b, user_sk):
        tx = b.create_transaction(b.me, user_sk, None, 'CREATE')

        assert sorted(tx) == ['id', 'transaction', 'version']
        assert sorted(tx['transaction']) == ['conditions', 'data', 'fulfillments', 'operation', 'timestamp']

    def test_create_transaction_with_unsupported_payload_raises(self, b):
        with pytest.raises(TypeError):
            b.create_transaction('a', 'b', 'c', 'd', payload=[])

    @pytest.mark.usefixtures('inputs')
    def test_create_transaction_transfer(self, b, user_vk, user_sk):
        input_tx = b.get_owned_ids(user_vk).pop()
        assert b.validate_fulfillments(b.get_transaction(input_tx['txid'])) == True

        tx = b.create_transaction(user_vk, b.me, input_tx, 'TRANSFER')

        assert sorted(tx) == ['id', 'transaction', 'version']
        assert sorted(tx['transaction']) == ['conditions', 'data', 'fulfillments', 'operation', 'timestamp']

        tx_signed = b.sign_transaction(tx, user_sk)

        assert b.validate_fulfillments(tx) == False
        assert b.validate_fulfillments(tx_signed) == True

    def test_transaction_hash(self, b, user_vk):
        payload = {'cats': 'are awesome'}
        tx = b.create_transaction(user_vk, user_vk, None, 'CREATE', payload)
        tx_calculated = {
            'conditions': [{'cid': 0,
                            'condition': tx['transaction']['conditions'][0]['condition'],
                            'new_owners': [user_vk]}],
            'data': {'hash': crypto.hash_data(util.serialize(payload)),
                     'payload': payload},
            'fulfillments': [{'current_owners': [user_vk],
                              'fid': 0,
                              'fulfillment': None,
                              'input': None}],
            'operation': 'CREATE',
            'timestamp': tx['transaction']['timestamp']
        }
        assert tx['transaction']['data'] == tx_calculated['data']
        # assert tx_hash == tx_calculated_hash

    def test_transaction_signature(self, b, user_sk, user_vk):
        tx = b.create_transaction(user_vk, user_vk, None, 'CREATE')
        tx_signed = b.sign_transaction(tx, user_sk)

        assert tx_signed['transaction']['fulfillments'][0]['fulfillment'] is not None
        assert b.validate_fulfillments(tx_signed)

    def test_serializer(self, b, user_vk):
        tx = b.create_transaction(user_vk, user_vk, None, 'CREATE')
        assert util.deserialize(util.serialize(tx)) == tx

    @pytest.mark.usefixtures('inputs')
    def test_write_transaction(self, b, user_vk, user_sk):
        input_tx = b.get_owned_ids(user_vk).pop()
        tx = b.create_transaction(user_vk, user_vk, input_tx, 'TRANSFER')
        tx_signed = b.sign_transaction(tx, user_sk)
        response = b.write_transaction(tx_signed)

        assert response['skipped'] == 0
        assert response['deleted'] == 0
        assert response['unchanged'] == 0
        assert response['errors'] == 0
        assert response['replaced'] == 0
        assert response['inserted'] == 1

    @pytest.mark.usefixtures('inputs')
    def test_read_transaction(self, b, user_vk, user_sk):
        input_tx = b.get_owned_ids(user_vk).pop()
        tx = b.create_transaction(user_vk, user_vk, input_tx, 'TRANSFER')
        tx_signed = b.sign_transaction(tx, user_sk)
        b.write_transaction(tx_signed)

        # create block and write it to the bighcain before retrieving the transaction
        block = b.create_block([tx_signed])
        b.write_block(block, durability='hard')

        response = b.get_transaction(tx_signed["id"])
        assert util.serialize(tx_signed) == util.serialize(response)

    @pytest.mark.usefixtures('inputs')
    def test_assign_transaction_one_node(self, b, user_vk, user_sk):
        input_tx = b.get_owned_ids(user_vk).pop()
        tx = b.create_transaction(user_vk, user_vk, input_tx, 'TRANSFER')
        tx_signed = b.sign_transaction(tx, user_sk)
        b.write_transaction(tx_signed)

        # retrieve the transaction
        response = r.table('backlog').get(tx_signed['id']).run(b.conn)

        # check if the assignee is the current node
        assert response['assignee'] == b.me

    @pytest.mark.usefixtures('inputs')
    def test_assign_transaction_multiple_nodes(self, b, user_vk, user_sk):
        # create 5 federation nodes
        for _ in range(5):
            b.federation_nodes.append(crypto.generate_key_pair()[1])

        # test assignee for several transactions
        for _ in range(20):
            input_tx = b.get_owned_ids(user_vk).pop()
            tx = b.create_transaction(user_vk, user_vk, input_tx, 'TRANSFER')
            tx_signed = b.sign_transaction(tx, user_sk)
            b.write_transaction(tx_signed)

            # retrieve the transaction
            response = r.table('backlog').get(tx_signed['id']).run(b.conn)

            # check if the assignee is the federation_nodes
            assert response['assignee'] in b.federation_nodes

    @pytest.mark.usefixtures('inputs')
    def test_genesis_block(self, b):
        response = list(r.table('bigchain')
                        .filter(r.row['block_number'] == 0)
                        .run(b.conn))[0]

        assert response['block_number'] == 0
        assert len(response['block']['transactions']) == 1
        assert response['block']['transactions'][0]['transaction']['operation'] == 'GENESIS'
        assert response['block']['transactions'][0]['transaction']['fulfillments'][0]['input'] is None

    def test_create_genesis_block_fails_if_table_not_empty(self, b):
        b.create_genesis_block()

        with pytest.raises(bigchaindb.core.GenesisBlockAlreadyExistsError):
            b.create_genesis_block()

        genesis_blocks = list(r.table('bigchain')
                              .filter(r.row['block_number'] == 0)
                              .run(b.conn))

        assert len(genesis_blocks) == 1

    @pytest.mark.skipif(reason='This test may not make sense after changing the chainification mode')
    def test_get_last_block(self, b):
        # get the number of blocks
        num_blocks = r.table('bigchain').count().run(b.conn)

        # get the last block
        last_block = b.get_last_block()

        assert last_block['block']['block_number'] == num_blocks - 1

    @pytest.mark.skipif(reason='This test may not make sense after changing the chainification mode')
    def test_get_last_block_id(self, b):
        last_block = b.get_last_block()
        last_block_id = b.get_last_block_id()

        assert last_block_id == last_block['id']

    @pytest.mark.skipif(reason='This test may not make sense after changing the chainification mode')
    def test_get_previous_block(self, b):
        last_block = b.get_last_block()
        new_block = b.create_block([])
        b.write_block(new_block, durability='hard')

        prev_block = b.get_previous_block(new_block)

        assert prev_block == last_block

    @pytest.mark.skipif(reason='This test may not make sense after changing the chainification mode')
    def test_get_previous_block_id(self, b):
        last_block = b.get_last_block()
        new_block = b.create_block([])
        b.write_block(new_block, durability='hard')

        prev_block_id = b.get_previous_block_id(new_block)

        assert prev_block_id == last_block['id']

    def test_create_new_block(self, b):
        new_block = b.create_block([])
        block_hash = crypto.hash_data(util.serialize(new_block['block']))

        assert new_block['block']['voters'] == [b.me]
        assert new_block['block']['node_pubkey'] == b.me
        assert crypto.VerifyingKey(b.me).verify(util.serialize(new_block['block']), new_block['signature']) is True
        assert new_block['id'] == block_hash
        assert new_block['votes'] == []

    def test_get_last_voted_block_returns_genesis_if_no_votes_has_been_casted(self, b):
        b.create_genesis_block()
        genesis = list(r.table('bigchain')
                       .filter(r.row['block_number'] == 0)
                       .run(b.conn))[0]
        assert b.get_last_voted_block() == genesis

    def test_get_last_voted_block_returns_the_correct_block(self, b):
        genesis = b.create_genesis_block()

        assert b.get_last_voted_block() == genesis

        block_1 = b.create_block([])
        block_2 = b.create_block([])
        block_3 = b.create_block([])

        b.write_block(block_1, durability='hard')
        b.write_block(block_2, durability='hard')
        b.write_block(block_3, durability='hard')

        b.write_vote(block_1, b.vote(block_1, b.get_last_voted_block(), True), 1)
        assert b.get_last_voted_block()['id'] == block_1['id']

        b.write_vote(block_2, b.vote(block_2, b.get_last_voted_block(), True), 2)
        assert b.get_last_voted_block()['id'] == block_2['id']

        b.write_vote(block_3, b.vote(block_3, b.get_last_voted_block(), True), 3)
        assert b.get_last_voted_block()['id'] == block_3['id']


class TestTransactionValidation(object):
    @pytest.mark.usefixtures('inputs')
    def test_create_operation_with_inputs(self, b, user_vk):
        input_tx = b.get_owned_ids(user_vk).pop()
        tx = b.create_transaction(b.me, user_vk, input_tx, 'CREATE')
        with pytest.raises(ValueError) as excinfo:
            b.validate_transaction(tx)

        assert excinfo.value.args[0] == 'A CREATE operation has no inputs'
        assert b.is_valid_transaction(tx) is False

    def test_create_operation_not_federation_node(self, b, user_vk):
        tx = b.create_transaction(user_vk, user_vk, None, 'CREATE')
        with pytest.raises(exceptions.OperationError) as excinfo:
            b.validate_transaction(tx)

        assert excinfo.value.args[0] == 'Only federation nodes can use the operation `CREATE`'
        assert b.is_valid_transaction(tx) is False

    def test_non_create_operation_no_inputs(self, b, user_vk):
        tx = b.create_transaction(user_vk, user_vk, None, 'TRANSFER')
        with pytest.raises(ValueError) as excinfo:
            b.validate_transaction(tx)

        assert excinfo.value.args[0] == 'Only `CREATE` transactions can have null inputs'
        assert b.is_valid_transaction(tx) is False

    def test_non_create_input_not_found(self, b, user_vk):
        tx = b.create_transaction(user_vk, user_vk, {'txid': 'c', 'cid': 0}, 'TRANSFER')
        with pytest.raises(exceptions.TransactionDoesNotExist) as excinfo:
            b.validate_transaction(tx)

        assert excinfo.value.args[0] == 'input `c` does not exist in the bigchain'
        assert b.is_valid_transaction(tx) is False

    @pytest.mark.usefixtures('inputs')
    def test_non_create_valid_input_wrong_owner(self, b, user_vk):
        input_valid = b.get_owned_ids(user_vk).pop()
        sk, vk = crypto.generate_key_pair()
        tx = b.create_transaction(vk, user_vk, input_valid, 'TRANSFER')
        with pytest.raises(exceptions.InvalidSignature) as excinfo:
            b.validate_transaction(tx)

        # assert excinfo.value.args[0] == 'current_owner `a` does not own the input `{}`'.format(valid_input)
        assert b.is_valid_transaction(tx) is False

    @pytest.mark.usefixtures('inputs')
    def test_non_create_double_spend(self, b, user_vk, user_sk):
        input_valid = b.get_owned_ids(user_vk).pop()
        tx_valid = b.create_transaction(user_vk, user_vk, input_valid, 'TRANSFER')
        tx_valid_signed = b.sign_transaction(tx_valid, user_sk)
        b.write_transaction(tx_valid_signed)

        # create and write block to bigchain
        block = b.create_block([tx_valid_signed])
        b.write_block(block, durability='hard')

        # create another transaction with the same input
        tx_double_spend = b.create_transaction(user_vk, user_vk, input_valid, 'TRANSFER')
        with pytest.raises(exceptions.DoubleSpend) as excinfo:
            b.validate_transaction(tx_double_spend)

        assert excinfo.value.args[0] == 'input `{}` was already spent'.format(input_valid)
        assert b.is_valid_transaction(tx_double_spend) is False

    @pytest.mark.usefixtures('inputs')
    def test_wrong_transaction_hash(self, b, user_vk):
        input_valid = b.get_owned_ids(user_vk).pop()
        tx_valid = b.create_transaction(user_vk, user_vk, input_valid, 'TRANSFER')

        # change the transaction hash
        tx_valid.update({'id': 'abcd'})
        with pytest.raises(exceptions.InvalidHash):
            b.validate_transaction(tx_valid)
        assert b.is_valid_transaction(tx_valid) is False

    @pytest.mark.usefixtures('inputs')
    def test_wrong_signature(self, b, user_sk, user_vk):
        input_valid = b.get_owned_ids(user_vk).pop()
        tx_valid = b.create_transaction(user_vk, user_vk, input_valid, 'TRANSFER')

        wrong_private_key = '4fyvJe1aw2qHZ4UNRYftXK7JU7zy9bCqoU5ps6Ne3xrY'

        with pytest.raises(exceptions.KeypairMismatchException):
            tx_invalid_signed = b.sign_transaction(tx_valid, wrong_private_key)

        # create a correctly signed transaction and change the signature
        tx_signed = b.sign_transaction(tx_valid, user_sk)
        fulfillment = tx_signed['transaction']['fulfillments'][0]['fulfillment']
        changed_fulfillment = cc.Ed25519Fulfillment().from_uri(fulfillment)
        changed_fulfillment.signature = b'0' * 64
        tx_signed['transaction']['fulfillments'][0]['fulfillment'] = changed_fulfillment.serialize_uri()

        with pytest.raises(exceptions.InvalidSignature):
            b.validate_transaction(tx_signed)
        assert b.is_valid_transaction(tx_signed) is False

    def test_valid_create_transaction(self, b, user_vk):
        tx = b.create_transaction(b.me, user_vk, None, 'CREATE')
        tx_signed = b.sign_transaction(tx, b.me_private)
        assert tx_signed == b.validate_transaction(tx_signed)
        assert tx_signed == b.is_valid_transaction(tx_signed)

    @pytest.mark.usefixtures('inputs')
    def test_valid_non_create_transaction(self, b, user_vk, user_sk):
        input_valid = b.get_owned_ids(user_vk).pop()
        tx_valid = b.create_transaction(user_vk, user_vk, input_valid, 'TRANSFER')

        tx_valid_signed = b.sign_transaction(tx_valid, user_sk)
        assert tx_valid_signed == b.validate_transaction(tx_valid_signed)
        assert tx_valid_signed == b.is_valid_transaction(tx_valid_signed)

    @pytest.mark.usefixtures('inputs')
    def test_valid_non_create_transaction_after_block_creation(self, b, user_vk, user_sk):
        input_valid = b.get_owned_ids(user_vk).pop()
        tx_valid = b.create_transaction(user_vk, user_vk, input_valid, 'TRANSFER')

        tx_valid_signed = b.sign_transaction(tx_valid, user_sk)
        assert tx_valid_signed == b.validate_transaction(tx_valid_signed)
        assert tx_valid_signed == b.is_valid_transaction(tx_valid_signed)

        # create block
        block = b.create_block([tx_valid_signed])
        assert b.is_valid_block(block)
        b.write_block(block, durability='hard')

        # check that the transaction is still valid after being written to the bigchain
        assert tx_valid_signed == b.validate_transaction(tx_valid_signed)
        assert tx_valid_signed == b.is_valid_transaction(tx_valid_signed)


class TestBlockValidation(object):
    def test_wrong_block_hash(self, b):
        block = b.create_block([])

        # change block hash
        block.update({'id': 'abc'})
        with pytest.raises(exceptions.InvalidHash):
            b.validate_block(block)

    @pytest.mark.skipif(reason='Separated tx validation from block creation.')
    @pytest.mark.usefixtures('inputs')
    def test_invalid_transactions_in_block(self, b, user_vk, ):
        # invalid transaction
        valid_input = b.get_owned_ids(user_vk).pop()
        tx_invalid = b.create_transaction('a', 'b', valid_input, 'c')

        block = b.create_block([tx_invalid])

        # create a block with invalid transactions
        block = {
            'timestamp': util.timestamp(),
            'transactions': [tx_invalid],
            'node_pubkey': b.me,
            'voters': b.federation_nodes
        }

        block_data = util.serialize(block)
        block_hash = crypto.hash_data(block_data)
        block_signature = crypto.SigningKey(b.me_private).sign(block_data)

        block = {
            'id': block_hash,
            'block': block,
            'signature': block_signature,
            'votes': []
        }

        with pytest.raises(exceptions.TransactionOwnerError) as excinfo:
            b.validate_block(block)

        assert excinfo.value.args[0] == 'current_owner `a` does not own the input `{}`'.format(valid_input)

    def test_invalid_block_id(self, b):
        block = b.create_block([])

        # change block hash
        block.update({'id': 'abc'})
        with pytest.raises(exceptions.InvalidHash):
            b.validate_block(block)

    @pytest.mark.usefixtures('inputs')
    def test_valid_block(self, b, user_vk, user_sk):
        # create valid transaction
        input_valid = b.get_owned_ids(user_vk).pop()
        tx_valid = b.create_transaction(user_vk, user_vk, input_valid, 'TRANSFER')
        tx_valid_signed = b.sign_transaction(tx_valid, user_sk)

        # create valid block
        block = b.create_block([tx_valid_signed])

        assert block == b.validate_block(block)
        assert b.is_valid_block(block)

    def test_invalid_signature(self, b):
        # create a valid block
        block = b.create_block([])

        # replace the block signature with an invalid one
        block['signature'] = crypto.SigningKey(b.me_private).sign(b'wrongdata')

        # check that validate_block raises an InvalidSignature exception
        with pytest.raises(exceptions.InvalidSignature):
            b.validate_block(block)

    def test_invalid_node_pubkey(self, b):
        # blocks can only be created by a federation node
        # create a valid block
        block = b.create_block([])

        # create some temp keys
        tmp_sk, tmp_vk = crypto.generate_key_pair()

        # change the block node_pubkey
        block['block']['node_pubkey'] = tmp_vk

        # just to make sure lets re-hash the block and create a valid signature
        # from a non federation node
        block['id'] = crypto.hash_data(util.serialize(block['block']))
        block['signature'] = crypto.SigningKey(tmp_sk).sign(util.serialize(block['block']))

        # check that validate_block raises an OperationError
        with pytest.raises(exceptions.OperationError):
            b.validate_block(block)


class TestBigchainVoter(object):
    def test_valid_block_voting(self, b):
        # create queue and voter
        q_new_block = mp.Queue()
        voter = Voter(q_new_block)

        genesis = b.create_genesis_block()
        # create valid block
        block = b.create_block([])
        # assert block is valid
        assert b.is_valid_block(block)
        b.write_block(block, durability='hard')

        # insert into queue
        # FIXME: we disable this because the voter can currently vote more than one time for a block
        # q_new_block.put(block)

        # vote
        voter.start()
        # wait for vote to be written
        time.sleep(1)
        voter.kill()

        # retrive block from bigchain
        bigchain_block = r.table('bigchain').get(block['id']).run(b.conn)

        # validate vote
        assert len(bigchain_block['votes']) == 1
        vote = bigchain_block['votes'][0]

        assert vote['vote']['voting_for_block'] == block['id']
        assert vote['vote']['previous_block'] == genesis['id']
        assert vote['vote']['is_block_valid'] is True
        assert vote['vote']['invalid_reason'] is None
        assert vote['node_pubkey'] == b.me
        assert crypto.VerifyingKey(b.me).verify(util.serialize(vote['vote']), vote['signature']) is True

    def test_invalid_block_voting(self, b, user_vk):
        # create queue and voter
        q_new_block = mp.Queue()
        voter = Voter(q_new_block)

        # create transaction
        transaction = b.create_transaction(b.me, user_vk, None, 'CREATE')
        transaction_signed = b.sign_transaction(transaction, b.me_private)

        genesis = b.create_genesis_block()
        # create invalid block
        block = b.create_block([transaction_signed])
        # change transaction id to make it invalid
        block['block']['transactions'][0]['id'] = 'abc'
        assert b.is_valid_block(block) is False
        b.write_block(block, durability='hard')

        # insert into queue
        # FIXME: we disable this because the voter can currently vote more than one time for a block
        # q_new_block.put(block)

        # vote
        voter.start()
        # wait for the vote to be written
        time.sleep(1)
        voter.kill()

        # retrive block from bigchain
        bigchain_block = r.table('bigchain').get(block['id']).run(b.conn)

        # validate vote
        assert len(bigchain_block['votes']) == 1
        vote = bigchain_block['votes'][0]

        assert vote['vote']['voting_for_block'] == block['id']
        assert vote['vote']['previous_block'] == genesis['id']
        assert vote['vote']['is_block_valid'] is False
        assert vote['vote']['invalid_reason'] is None
        assert vote['node_pubkey'] == b.me
        assert crypto.VerifyingKey(b.me).verify(util.serialize(vote['vote']), vote['signature']) is True

    def test_vote_creation_valid(self, b):
        # create valid block
        block = b.create_block([])
        # retrieve vote
        vote = b.vote(block, 'abc', True)

        # assert vote is correct
        assert vote['vote']['voting_for_block'] == block['id']
        assert vote['vote']['previous_block'] == 'abc'
        assert vote['vote']['is_block_valid'] is True
        assert vote['vote']['invalid_reason'] is None
        assert vote['node_pubkey'] == b.me
        assert crypto.VerifyingKey(b.me).verify(util.serialize(vote['vote']), vote['signature']) is True

    def test_vote_creation_invalid(self, b):
        # create valid block
        block = b.create_block([])
        # retrieve vote
        vote = b.vote(block, 'abc', False)

        # assert vote is correct
        assert vote['vote']['voting_for_block'] == block['id']
        assert vote['vote']['previous_block'] == 'abc'
        assert vote['vote']['is_block_valid'] is False
        assert vote['vote']['invalid_reason'] is None
        assert vote['node_pubkey'] == b.me
        assert crypto.VerifyingKey(b.me).verify(util.serialize(vote['vote']), vote['signature']) is True


class TestBigchainBlock(object):
    def test_by_assignee(self, b, user_vk):
        # create transactions and randomly assigne them
        transactions = mp.Queue()
        count_assigned_to_me = 0
        for i in range(100):
            tx = b.create_transaction(b.me, user_vk, None, 'CREATE')
            assignee = random.choice([b.me, 'aaa', 'bbb', 'ccc'])
            if assignee == b.me:
                count_assigned_to_me += 1

            tx['assignee'] = assignee
            transactions.put(tx)
        transactions.put('stop')

        # create a block instance
        block = Block(transactions)
        block.q_new_transaction = transactions
        # filter the transactions
        block.filter_by_assignee()

        # check if the number of transactions assigned to the node is the same as the number in
        # the queue minus 'stop'
        assert block.q_tx_to_validate.qsize() - 1 == count_assigned_to_me

    def test_validate_transactions(self, b, user_vk):
        # create transactions and randomly invalidate some of them by changing the hash
        transactions = mp.Queue()
        count_valid = 0
        for i in range(100):
            valid = random.choice([True, False])
            tx = b.create_transaction(b.me, user_vk, None, 'CREATE')
            tx = b.sign_transaction(tx, b.me_private)
            if not valid:
                tx['id'] = 'a' * 64
            else:
                count_valid += 1
            transactions.put(tx)
        transactions.put('stop')

        # create a block instance
        block = Block(transactions)
        block.q_tx_to_validate = transactions
        # validate transactions
        block.validate_transactions()

        # check if the number of valid transactions
        assert block.q_tx_validated.qsize() - 1 == count_valid
        assert block.q_tx_delete.qsize() - 1 == 100

    def test_create_block(self, b, user_vk):
        # create transactions
        transactions = mp.Queue()
        for i in range(100):
            tx = b.create_transaction(b.me, user_vk, None, 'CREATE')
            tx = b.sign_transaction(tx, b.me_private)
            transactions.put(tx)
        transactions.put('stop')

        # create a block instance
        block = Block(transactions)
        block.q_tx_validated = transactions
        # create blocks
        block.create_blocks()

        # check if the number of valid transactions
        assert block.q_block.qsize() - 1 == 1

    def test_write_block(self, b, user_vk):
        # create transactions
        transactions = []
        blocks = mp.Queue()
        for i in range(100):
            tx = b.create_transaction(b.me, user_vk, None, 'CREATE')
            tx = b.sign_transaction(tx, b.me_private)
            transactions.append(tx)

        # create block
        block = b.create_block(transactions)
        blocks.put(block)
        blocks.put('stop')

        # create a block instance
        block = Block(transactions)
        block.q_block = blocks

        # make sure that we only have the genesis block in bigchain
        r.table('bigchain').delete().run(b.conn)
        b.create_genesis_block()

        # write blocks
        block.write_blocks()
        # lets give it some time for the block to be written
        time.sleep(1)

        # check if the number of blocks in bigchain increased
        assert r.table('bigchain').count() == 2

    def test_delete_transactions(self, b, user_vk):
        # make sure that there are no transactions in the backlog
        r.table('backlog').delete().run(b.conn)

        # create and write transactions to the backlog
        transactions = mp.Queue()
        for i in range(100):
            tx = b.create_transaction(b.me, user_vk, None, 'CREATE')
            tx = b.sign_transaction(tx, b.me_private)
            b.write_transaction(tx)
            transactions.put(tx['id'])
        transactions.put('stop')

        # create a block instance
        block = Block(transactions)
        block.q_tx_delete = transactions

        # make sure that there are transactions on the backlog
        r.table('backlog').count().run(b.conn) == 100

        # run the delete process
        block.delete_transactions()
        # give the db time
        time.sleep(1)

        # check if all transactions were deleted from the backlog
        assert r.table('backlog').count() == 0

    def test_bootstrap(self, b, user_vk):
        # make sure that there are no transactions in the backlog
        r.table('backlog').delete().run(b.conn)

        # create and write transactions to the backlog
        for i in range(100):
            tx = b.create_transaction(b.me, user_vk, None, 'CREATE')
            tx = b.sign_transaction(tx, b.me_private)
            b.write_transaction(tx)

        # create a block instance
        block = Block(None)

        # run bootstrap
        initial_results = block.bootstrap()

        # we should have gotten a queue with 100 results minus the poison pills
        assert initial_results.qsize() - mp.cpu_count() == 100

    def test_start(self, b, user_vk):
        # start with 100 transactions in the backlog and 100 in the changefeed

        # make sure that there are no transactions in the backlog
        r.table('backlog').delete().run(b.conn)

        # create and write transactions to the backlog
        for i in range(100):
            tx = b.create_transaction(b.me, user_vk, None, 'CREATE')
            tx = b.sign_transaction(tx, b.me_private)
            b.write_transaction(tx)

        # create 100 more transactions to emulate the changefeed
        new_transactions = mp.Queue()
        for i in range(100):
            tx = b.create_transaction(b.me, user_vk, None, 'CREATE')
            tx = b.sign_transaction(tx, b.me_private)
            b.write_transaction(tx)
            new_transactions.put(tx)

        for i in range(mp.cpu_count()):
            new_transactions.put('stop')

        # create a block instance
        block = Block(new_transactions)

        # start the block processes
        block.start()

        time.sleep(6)

        assert new_transactions.qsize() == 0
        assert r.table('backlog').count() == 0
        assert r.table('bigchain').count() == 2

    def test_empty_queues(self, b):
        # create empty queue
        new_transactions = mp.Queue()

        # create block instance
        block = Block(new_transactions)

        # start block process
        block.start()

        # wait for 6 seconds to give it time for an empty queue exception to occur
        time.sleep(6)

        # join the process
        block.kill()

    def test_duplicated_transactions(self):
        pytest.skip('We may have duplicates in the initial_results and changefeed')


class TestMultipleInputs(object):
    def test_transfer_single_owners_single_input(self, b, user_sk, user_vk, inputs):
        # create a new user
        user2_sk, user2_vk = crypto.generate_key_pair()

        # get inputs
        owned_inputs = b.get_owned_ids(user_vk)
        inp = owned_inputs.pop()

        # create a transaction
        tx = b.create_transaction([user_vk], [user2_sk], inp, 'TRANSFER')
        tx_signed = b.sign_transaction(tx, user_sk)

        # validate transaction
        assert b.is_valid_transaction(tx_signed) == tx_signed
        assert len(tx_signed['transaction']['fulfillments']) == 1
        assert len(tx_signed['transaction']['conditions']) == 1

    def test_transfer_single_owners_multiple_inputs(self, b, user_sk, user_vk):
        # create a new user
        user2_sk, user2_vk = crypto.generate_key_pair()

        # create inputs to spend
        transactions = []
        for i in range(10):
            tx = b.create_transaction(b.me, user_vk, None, 'CREATE')
            tx_signed = b.sign_transaction(tx, b.me_private)
            transactions.append(tx_signed)
            b.write_transaction(tx_signed)
        block = b.create_block(transactions)
        b.write_block(block, durability='hard')

        # get inputs
        owned_inputs = b.get_owned_ids(user_vk)
        inputs = owned_inputs[:3]

        # create a transaction
        tx = b.create_transaction(user_vk, user2_vk, inputs, 'TRANSFER')
        tx_signed = b.sign_transaction(tx, user_sk)

        # validate transaction
        assert b.is_valid_transaction(tx_signed) == tx_signed
        assert len(tx_signed['transaction']['fulfillments']) == 3
        assert len(tx_signed['transaction']['conditions']) == 3

    def test_transfer_single_owners_single_input_from_multiple_outputs(self, b, user_sk, user_vk):
        # create a new user
        user2_sk, user2_vk = crypto.generate_key_pair()

        # create inputs to spend
        transactions = []
        for i in range(10):
            tx = b.create_transaction(b.me, user_vk, None, 'CREATE')
            tx_signed = b.sign_transaction(tx, b.me_private)
            transactions.append(tx_signed)
            b.write_transaction(tx_signed)
        block = b.create_block(transactions)
        b.write_block(block, durability='hard')

        # get inputs
        owned_inputs = b.get_owned_ids(user_vk)
        inputs = owned_inputs[:3]

        # create a transaction
        tx = b.create_transaction(user_vk, user2_vk, inputs, 'TRANSFER')
        tx_signed = b.sign_transaction(tx, user_sk)

        # create block with the transaction
        block = b.create_block([tx_signed])
        b.write_block(block, durability='hard')

        # get inputs from user2
        owned_inputs = b.get_owned_ids(user2_vk)
        assert len(owned_inputs) == 3

        # create a transaction with a single input from a multiple output transaction
        inp = owned_inputs.pop()
        tx = b.create_transaction(user2_vk, user_vk, inp, 'TRANSFER')
        tx_signed = b.sign_transaction(tx, user2_sk)

        assert b.is_valid_transaction(tx_signed) == tx_signed
        assert len(tx_signed['transaction']['fulfillments']) == 1
        assert len(tx_signed['transaction']['conditions']) == 1

    def test_single_current_owner_multiple_new_owners_single_input(self, b, user_sk, user_vk, inputs):
        # create a new users
        user2_sk, user2_vk = crypto.generate_key_pair()
        user3_sk, user3_vk = crypto.generate_key_pair()

        # get inputs
        owned_inputs = b.get_owned_ids(user_vk)
        inp = owned_inputs.pop()

        # create a transaction
        tx = b.create_transaction(user_vk, [user2_sk, user3_vk], inp, 'TRANSFER')
        tx_signed = b.sign_transaction(tx, user_sk)

        # validate transaction
        assert b.is_valid_transaction(tx_signed) == tx_signed
        assert len(tx_signed['transaction']['fulfillments']) == 1
        assert len(tx_signed['transaction']['conditions']) == 1

    def test_single_current_owner_multiple_new_owners_multiple_inputs(self, b, user_sk, user_vk):
        # create a new users
        user2_sk, user2_vk = crypto.generate_key_pair()
        user3_sk, user3_vk = crypto.generate_key_pair()

        # create inputs to spend
        transactions = []
        for i in range(5):
            tx = b.create_transaction(b.me, user_vk, None, 'CREATE')
            tx_signed = b.sign_transaction(tx, b.me_private)
            transactions.append(tx_signed)
            b.write_transaction(tx_signed)
        block = b.create_block(transactions)
        b.write_block(block, durability='hard')

        # get inputs
        owned_inputs = b.get_owned_ids(user_vk)
        inputs = owned_inputs[:3]

        # create a transaction
        tx = b.create_transaction(user_vk, [user2_vk, user3_vk], inputs, 'TRANSFER')
        tx_signed = b.sign_transaction(tx, user_sk)

        # validate transaction
        assert b.is_valid_transaction(tx_signed) == tx_signed
        assert len(tx_signed['transaction']['fulfillments']) == 3
        assert len(tx_signed['transaction']['conditions']) == 3

    def test_multiple_current_owners_single_new_owner_single_input(self, b, user_sk, user_vk):
        # create a new users
        user2_sk, user2_vk = crypto.generate_key_pair()
        user3_sk, user3_vk = crypto.generate_key_pair()

        # create input to spend
        tx = b.create_transaction(b.me, [user_vk, user2_vk], None, 'CREATE')
        tx_signed = b.sign_transaction(tx, b.me_private)
        block = b.create_block([tx_signed])
        b.write_block(block, durability='hard')

        # get input
        owned_inputs = b.get_owned_ids(user_vk)
        inp = owned_inputs[0]

        # create a transaction
        tx = b.create_transaction([user_vk, user2_vk], user3_vk, inp, 'TRANSFER')
        tx_signed = b.sign_transaction(tx, [user_sk, user2_sk])

        # validate transaction
        assert b.is_valid_transaction(tx_signed) == tx_signed
        assert len(tx_signed['transaction']['fulfillments']) == 1
        assert len(tx_signed['transaction']['conditions']) == 1

    def test_multiple_current_owners_single_new_owner_multiple_inputs(self, b, user_sk, user_vk):
        # create a new users
        user2_sk, user2_vk = crypto.generate_key_pair()
        user3_sk, user3_vk = crypto.generate_key_pair()

        # create inputs to spend
        transactions = []
        for i in range(5):
            tx = b.create_transaction(b.me, [user_vk, user2_vk], None, 'CREATE')
            tx_signed = b.sign_transaction(tx, b.me_private)
            transactions.append(tx_signed)
        block = b.create_block(transactions)
        b.write_block(block, durability='hard')

        # get input
        owned_inputs = b.get_owned_ids(user_vk)
        inputs = owned_inputs[:3]

        # create a transaction
        tx = b.create_transaction([user_vk, user2_vk], user3_vk, inputs, 'TRANSFER')
        tx_signed = b.sign_transaction(tx, [user_sk, user2_sk])

        # validate transaction
        assert b.is_valid_transaction(tx_signed) == tx_signed
        assert len(tx_signed['transaction']['fulfillments']) == 3
        assert len(tx_signed['transaction']['conditions']) == 3

    def test_multiple_current_owners_multiple_new_owners_single_input(self, b, user_sk, user_vk):
        # create a new users
        user2_sk, user2_vk = crypto.generate_key_pair()
        user3_sk, user3_vk = crypto.generate_key_pair()
        user4_sk, user4_vk = crypto.generate_key_pair()

        # create input to spend
        tx = b.create_transaction(b.me, [user_vk, user2_vk], None, 'CREATE')
        tx_signed = b.sign_transaction(tx, b.me_private)
        block = b.create_block([tx_signed])
        b.write_block(block, durability='hard')

        # get input
        owned_inputs = b.get_owned_ids(user_vk)
        inp = owned_inputs[0]

        # create a transaction
        tx = b.create_transaction([user_vk, user2_vk], [user3_vk, user4_vk], inp, 'TRANSFER')
        tx_signed = b.sign_transaction(tx, [user_sk, user2_sk])

        # validate transaction
        assert b.is_valid_transaction(tx_signed) == tx_signed
        assert len(tx_signed['transaction']['fulfillments']) == 1
        assert len(tx_signed['transaction']['conditions']) == 1

    def test_multiple_current_owners_multiple_new_owners_multiple_inputs(self, b, user_sk, user_vk):
        # create a new users
        user2_sk, user2_vk = crypto.generate_key_pair()
        user3_sk, user3_vk = crypto.generate_key_pair()
        user4_sk, user4_vk = crypto.generate_key_pair()

        # create inputs to spend
        transactions = []
        for i in range(5):
            tx = b.create_transaction(b.me, [user_vk, user2_vk], None, 'CREATE')
            tx_signed = b.sign_transaction(tx, b.me_private)
            transactions.append(tx_signed)
        block = b.create_block(transactions)
        b.write_block(block, durability='hard')

        # get input
        owned_inputs = b.get_owned_ids(user_vk)
        inp = owned_inputs[:3]

        # create a transaction
        tx = b.create_transaction([user_vk, user2_vk], [user3_vk, user4_vk], inp, 'TRANSFER')
        tx_signed = b.sign_transaction(tx, [user_sk, user2_sk])

        # validate transaction
        assert b.is_valid_transaction(tx_signed) == tx_signed
        assert len(tx_signed['transaction']['fulfillments']) == 3
        assert len(tx_signed['transaction']['conditions']) == 3

    def test_get_owned_ids_single_tx_single_output(self, b, user_sk, user_vk):
        # create a new users
        user2_sk, user2_vk = crypto.generate_key_pair()

        # create input to spend
        tx = b.create_transaction(b.me, user_vk, None, 'CREATE')
        tx_signed = b.sign_transaction(tx, b.me_private)
        block = b.create_block([tx_signed])
        b.write_block(block, durability='hard')

        # get input
        owned_inputs_user1 = b.get_owned_ids(user_vk)
        owned_inputs_user2 = b.get_owned_ids(user2_vk)
        assert owned_inputs_user1 == [{'cid': 0, 'txid': tx['id']}]
        assert owned_inputs_user2 == []

        # create a transaction and block
        tx = b.create_transaction(user_vk, user2_vk, owned_inputs_user1, 'TRANSFER')
        tx_signed = b.sign_transaction(tx, user_sk)
        block = b.create_block([tx_signed])
        b.write_block(block, durability='hard')

        owned_inputs_user1 = b.get_owned_ids(user_vk)
        owned_inputs_user2 = b.get_owned_ids(user2_vk)
        assert owned_inputs_user1 == []
        assert owned_inputs_user2 == [{'cid': 0, 'txid': tx['id']}]

    def test_get_owned_ids_single_tx_multiple_outputs(self, b, user_sk, user_vk):
        # create a new users
        user2_sk, user2_vk = crypto.generate_key_pair()

        # create inputs to spend
        transactions = []
        for i in range(5):
            tx = b.create_transaction(b.me, user_vk, None, 'CREATE')
            tx_signed = b.sign_transaction(tx, b.me_private)
            transactions.append(tx_signed)
        block = b.create_block(transactions)
        b.write_block(block, durability='hard')

        # get input
        owned_inputs_user1 = b.get_owned_ids(user_vk)
        owned_inputs_user2 = b.get_owned_ids(user2_vk)

        expected_owned_inputs_user1 = [{'txid': tx['id'], 'cid': 0} for tx in transactions]
        assert owned_inputs_user1 == expected_owned_inputs_user1
        assert owned_inputs_user2 == []

        # create a transaction and block
        tx = b.create_transaction(user_vk, user2_vk,
                                  [expected_owned_inputs_user1.pop(), expected_owned_inputs_user1.pop()], 'TRANSFER')
        tx_signed = b.sign_transaction(tx, user_sk)
        block = b.create_block([tx_signed])
        b.write_block(block, durability='hard')

        owned_inputs_user1 = b.get_owned_ids(user_vk)
        owned_inputs_user2 = b.get_owned_ids(user2_vk)
        assert owned_inputs_user1 == expected_owned_inputs_user1
        assert owned_inputs_user2 == [{'cid': 0, 'txid': tx['id']}, {'cid': 1, 'txid': tx['id']}]

    def test_get_owned_ids_multiple_owners(self, b, user_sk, user_vk):
        # create a new users
        user2_sk, user2_vk = crypto.generate_key_pair()
        user3_sk, user3_vk = crypto.generate_key_pair()

        # create inputs to spend
        transactions = []
        for i in range(5):
            tx = b.create_transaction(b.me, [user_vk, user2_vk], None, 'CREATE')
            tx_signed = b.sign_transaction(tx, b.me_private)
            transactions.append(tx_signed)
        block = b.create_block(transactions)
        b.write_block(block, durability='hard')

        # get input
        owned_inputs_user1 = b.get_owned_ids(user_vk)
        owned_inputs_user2 = b.get_owned_ids(user2_vk)
        expected_owned_inputs_user1 = [{'txid': tx['id'], 'cid': 0} for tx in transactions]
        assert owned_inputs_user1 == owned_inputs_user2
        assert owned_inputs_user1 == expected_owned_inputs_user1

        # create a transaction
        tx = b.create_transaction([user_vk, user2_vk], user3_vk, expected_owned_inputs_user1.pop(), 'TRANSFER')
        tx_signed = b.sign_transaction(tx, [user_sk, user2_sk])
        block = b.create_block([tx_signed])
        b.write_block(block, durability='hard')

        owned_inputs_user1 = b.get_owned_ids(user_vk)
        owned_inputs_user2 = b.get_owned_ids(user2_vk)
        assert owned_inputs_user1 == owned_inputs_user2
        assert owned_inputs_user1 == expected_owned_inputs_user1

    def test_get_spent_single_tx_single_output(self, b, user_sk, user_vk):
        # create a new users
        user2_sk, user2_vk = crypto.generate_key_pair()

        # create input to spend
        tx = b.create_transaction(b.me, user_vk, None, 'CREATE')
        tx_signed = b.sign_transaction(tx, b.me_private)
        block = b.create_block([tx_signed])
        b.write_block(block, durability='hard')

        # get input
        owned_inputs_user1 = b.get_owned_ids(user_vk)

        # check spents
        spent_inputs_user1 = b.get_spent(owned_inputs_user1[0])
        assert spent_inputs_user1 is None

        # create a transaction and block
        tx = b.create_transaction(user_vk, user2_vk, owned_inputs_user1, 'TRANSFER')
        tx_signed = b.sign_transaction(tx, user_sk)
        block = b.create_block([tx_signed])
        b.write_block(block, durability='hard')

        spent_inputs_user1 = b.get_spent(owned_inputs_user1[0])
        assert spent_inputs_user1 == tx_signed

    def test_get_spent_single_tx_multiple_outputs(self, b, user_sk, user_vk):
        # create a new users
        user2_sk, user2_vk = crypto.generate_key_pair()

        # create inputs to spend
        transactions = []
        for i in range(5):
            tx = b.create_transaction(b.me, user_vk, None, 'CREATE')
            tx_signed = b.sign_transaction(tx, b.me_private)
            transactions.append(tx_signed)
        block = b.create_block(transactions)
        b.write_block(block, durability='hard')

        # get input
        owned_inputs_user1 = b.get_owned_ids(user_vk)

        # check spents
        for inp in owned_inputs_user1:
            assert b.get_spent(inp) is None

        # select inputs to use
        inputs = [owned_inputs_user1.pop(), owned_inputs_user1.pop()]

        # create a transaction and block
        tx = b.create_transaction(user_vk, user2_vk, inputs, 'TRANSFER')
        tx_signed = b.sign_transaction(tx, user_sk)
        block = b.create_block([tx_signed])
        b.write_block(block, durability='hard')

        # check that used inputs are marked as spent
        for inp in inputs:
            assert b.get_spent(inp) == tx_signed

        # check that the other remain marked as unspent
        for inp in owned_inputs_user1:
            assert b.get_spent(inp) is None

    def test_get_spent_multiple_owners(self, b, user_sk, user_vk):
        # create a new users
        user2_sk, user2_vk = crypto.generate_key_pair()
        user3_sk, user3_vk = crypto.generate_key_pair()

        # create inputs to spend
        transactions = []
        for i in range(5):
            tx = b.create_transaction(b.me, [user_vk, user2_vk], None, 'CREATE')
            tx_signed = b.sign_transaction(tx, b.me_private)
            transactions.append(tx_signed)
        block = b.create_block(transactions)
        b.write_block(block, durability='hard')

        # get input
        owned_inputs_user1 = b.get_owned_ids(user_vk)

        # check spents
        for inp in owned_inputs_user1:
            assert b.get_spent(inp) is None

        # select inputs to use
        inputs = [owned_inputs_user1.pop()]

        # create a transaction
        tx = b.create_transaction([user_vk, user2_vk], user3_vk, inputs, 'TRANSFER')
        tx_signed = b.sign_transaction(tx, [user_sk, user2_sk])
        block = b.create_block([tx_signed])
        b.write_block(block, durability='hard')

        # check that used inputs are marked as spent
        for inp in inputs:
            assert b.get_spent(inp) == tx_signed

        # check that the other remain marked as unspent
        for inp in owned_inputs_user1:
            assert b.get_spent(inp) is None


class TestCryptoconditions(object):
    def test_fulfillment_transaction_create(self, b, user_vk):
        tx = b.create_transaction(b.me, user_vk, None, 'CREATE')
        condition = tx['transaction']['conditions'][0]['condition']
        condition_from_uri = cc.Condition.from_uri(condition['uri'])
        condition_from_json = cc.Fulfillment.from_json(condition['details']).condition

        assert condition_from_uri.serialize_uri() == condition_from_json.serialize_uri()
        assert condition['details']['public_key'] == user_vk

        tx_signed = b.sign_transaction(tx, b.me_private)
        fulfillment = tx_signed['transaction']['fulfillments'][0]
        fulfillment_from_uri = cc.Fulfillment.from_uri(fulfillment['fulfillment'])

        assert fulfillment['current_owners'][0] == b.me
        assert fulfillment_from_uri.public_key.to_ascii().decode() == b.me
        assert b.validate_fulfillments(tx_signed) == True
        assert b.is_valid_transaction(tx_signed) == tx_signed

    @pytest.mark.usefixtures('inputs')
    def test_fulfillment_transaction_transfer(self, b, user_vk, user_sk):
        # create valid transaction
        other_sk, other_vk = crypto.generate_key_pair()
        prev_tx_id = b.get_owned_ids(user_vk).pop()
        tx = b.create_transaction(user_vk, other_vk, prev_tx_id, 'TRANSFER')

        prev_tx = b.get_transaction(prev_tx_id['txid'])
        prev_condition = prev_tx['transaction']['conditions'][0]['condition']
        prev_condition_from_uri = cc.Condition.from_uri(prev_condition['uri'])
        prev_condition_from_json = cc.Fulfillment.from_json(prev_condition['details']).condition

        assert prev_condition_from_uri.serialize_uri() == prev_condition_from_json.serialize_uri()
        assert prev_condition['details']['public_key'] == user_vk

        condition = tx['transaction']['conditions'][0]['condition']
        condition_from_uri = cc.Condition.from_uri(condition['uri'])
        condition_from_json = cc.Fulfillment.from_json(condition['details']).condition

        assert condition_from_uri.serialize_uri() == condition_from_json.serialize_uri()
        assert condition['details']['public_key'] == other_vk

        tx_signed = b.sign_transaction(tx, user_sk)
        fulfillment = tx_signed['transaction']['fulfillments'][0]
        fulfillment_from_uri = cc.Fulfillment.from_uri(fulfillment['fulfillment'])

        assert fulfillment['current_owners'][0] == user_vk
        assert fulfillment_from_uri.public_key.to_ascii().decode() == user_vk
        assert fulfillment_from_uri.condition.serialize_uri() == prev_condition['uri']
        assert b.validate_fulfillments(tx_signed) == True
        assert b.is_valid_transaction(tx_signed) == tx_signed

    def test_override_condition_create(self, b, user_vk):
        tx = b.create_transaction(b.me, user_vk, None, 'CREATE')
        fulfillment = cc.Ed25519Fulfillment(public_key=user_vk)
        tx['transaction']['conditions'][0]['condition'] = {
            'details': json.loads(fulfillment.serialize_json()),
            'uri': fulfillment.condition.serialize_uri()
        }

        tx_signed = b.sign_transaction(tx, b.me_private)

        fulfillment = tx_signed['transaction']['fulfillments'][0]
        fulfillment_from_uri = cc.Fulfillment.from_uri(fulfillment['fulfillment'])

        assert fulfillment['current_owners'][0] == b.me
        assert fulfillment_from_uri.public_key.to_ascii().decode() == b.me
        assert b.validate_fulfillments(tx_signed) == True
        assert b.is_valid_transaction(tx_signed) == tx_signed

    @pytest.mark.usefixtures('inputs')
    def test_override_condition_transfer(self, b, user_vk, user_sk):
        # create valid transaction
        other_sk, other_vk = crypto.generate_key_pair()
        prev_tx_id = b.get_owned_ids(user_vk).pop()
        tx = b.create_transaction(user_vk, other_vk, prev_tx_id, 'TRANSFER')

        fulfillment = cc.Ed25519Fulfillment(public_key=other_vk)
        tx['transaction']['conditions'][0]['condition'] = {
            'details': json.loads(fulfillment.serialize_json()),
            'uri': fulfillment.condition.serialize_uri()
        }

        tx_signed = b.sign_transaction(tx, user_sk)
        fulfillment = tx_signed['transaction']['fulfillments'][0]
        fulfillment_from_uri = cc.Fulfillment.from_uri(fulfillment['fulfillment'])

        assert fulfillment['current_owners'][0] == user_vk
        assert fulfillment_from_uri.public_key.to_ascii().decode() == user_vk
        assert b.validate_fulfillments(tx_signed) == True
        assert b.is_valid_transaction(tx_signed) == tx_signed

    def test_override_fulfillment_create(self, b, user_vk):
        tx = b.create_transaction(b.me, user_vk, None, 'CREATE')
        original_fulfillment = tx['transaction']['fulfillments'][0]
        fulfillment_message = util.get_fulfillment_message(tx, original_fulfillment, serialized=True)
        fulfillment = cc.Ed25519Fulfillment(public_key=b.me)
        fulfillment.sign(fulfillment_message, crypto.SigningKey(b.me_private))

        tx['transaction']['fulfillments'][0]['fulfillment'] = fulfillment.serialize_uri()

        assert b.validate_fulfillments(tx) == True
        assert b.is_valid_transaction(tx) == tx

    @pytest.mark.usefixtures('inputs')
    def test_override_fulfillment_transfer(self,  b, user_vk, user_sk):
        # create valid transaction
        other_sk, other_vk = crypto.generate_key_pair()
        prev_tx_id = b.get_owned_ids(user_vk).pop()
        tx = b.create_transaction(user_vk, other_vk, prev_tx_id, 'TRANSFER')

        original_fulfillment = tx['transaction']['fulfillments'][0]
        fulfillment_message = util.get_fulfillment_message(tx, original_fulfillment, serialized=True)
        fulfillment = cc.Ed25519Fulfillment(public_key=user_vk)
        fulfillment.sign(fulfillment_message, crypto.SigningKey(user_sk))

        tx['transaction']['fulfillments'][0]['fulfillment'] = fulfillment.serialize_uri()

        assert b.validate_fulfillments(tx) == True
        assert b.is_valid_transaction(tx) == tx

    @pytest.mark.usefixtures('inputs')
    def test_override_condition_and_fulfillment_transfer(self,  b, user_vk, user_sk):
        other_sk, other_vk = crypto.generate_key_pair()
        first_input_tx = b.get_owned_ids(user_vk).pop()
        first_tx = b.create_transaction(user_vk, other_vk, first_input_tx, 'TRANSFER')

        first_tx_condition = cc.Ed25519Fulfillment(public_key=other_vk)
        first_tx['transaction']['conditions'][0]['condition'] = {
            'details': json.loads(first_tx_condition.serialize_json()),
            'uri': first_tx_condition.condition.serialize_uri()
        }

        first_tx_fulfillment = first_tx['transaction']['fulfillments'][0]
        first_tx_fulfillment_message = util.get_fulfillment_message(first_tx, first_tx_fulfillment, serialized=True)
        first_tx_fulfillment = cc.Ed25519Fulfillment(public_key=user_vk)
        first_tx_fulfillment.sign(first_tx_fulfillment_message, crypto.SigningKey(user_sk))
        first_tx['transaction']['fulfillments'][0]['fulfillment'] = first_tx_fulfillment.serialize_uri()

        assert b.validate_transaction(first_tx) == first_tx
        assert b.is_valid_transaction(first_tx) == first_tx

        b.write_transaction(first_tx)

        # create and write block to bigchain
        block = b.create_block([first_tx])
        b.write_block(block, durability='hard')

        next_input_tx = b.get_owned_ids(other_vk).pop()
        # create another transaction with the same input
        next_tx = b.create_transaction(other_vk, user_vk, next_input_tx, 'TRANSFER')

        next_tx_fulfillment = next_tx['transaction']['fulfillments'][0]
        next_tx_fulfillment_message = util.get_fulfillment_message(next_tx, next_tx_fulfillment, serialized=True)
        next_tx_fulfillment = cc.Ed25519Fulfillment(public_key=other_vk)
        next_tx_fulfillment.sign(next_tx_fulfillment_message, crypto.SigningKey(other_sk))
        next_tx['transaction']['fulfillments'][0]['fulfillment'] = next_tx_fulfillment.serialize_uri()

        assert b.validate_transaction(next_tx) == next_tx
        assert b.is_valid_transaction(next_tx) == next_tx

    @pytest.mark.usefixtures('inputs')
    def test_override_condition_and_fulfillment_transfer_threshold(self, b, user_vk, user_sk):
        other1_sk, other1_vk = crypto.generate_key_pair()
        other2_sk, other2_vk = crypto.generate_key_pair()
        other3_sk, other3_vk = crypto.generate_key_pair()

        first_input_tx = b.get_owned_ids(user_vk).pop()
        first_tx = b.create_transaction(user_vk, [other1_vk, other2_vk, other3_vk], first_input_tx, 'TRANSFER')

        first_tx_condition = cc.ThresholdSha256Fulfillment(threshold=2)
        first_tx_condition.add_subfulfillment(cc.Ed25519Fulfillment(public_key=other1_vk))
        first_tx_condition.add_subfulfillment(cc.Ed25519Fulfillment(public_key=other2_vk))
        first_tx_condition.add_subfulfillment(cc.Ed25519Fulfillment(public_key=other3_vk))

        first_tx['transaction']['conditions'][0]['condition'] = {
            'details': json.loads(first_tx_condition.serialize_json()),
            'uri': first_tx_condition.condition.serialize_uri()
        }
        # conditions have been updated, so hash needs updating
        first_tx['id'] = util.get_hash_data(first_tx)

        first_tx_signed = b.sign_transaction(first_tx, user_sk)

        assert b.validate_transaction(first_tx_signed) == first_tx_signed
        assert b.is_valid_transaction(first_tx_signed) == first_tx_signed

        b.write_transaction(first_tx_signed)

        # create and write block to bigchain
        block = b.create_block([first_tx])
        b.write_block(block, durability='hard')

        next_input_tx = b.get_owned_ids(other1_vk).pop()
        # create another transaction with the same input
        next_tx = b.create_transaction([other1_vk, other2_vk, other3_vk], user_vk, next_input_tx, 'TRANSFER')

        next_tx_fulfillment = next_tx['transaction']['fulfillments'][0]
        next_tx_fulfillment_message = util.get_fulfillment_message(next_tx, next_tx_fulfillment, serialized=True)
        next_tx_fulfillment = cc.ThresholdSha256Fulfillment(threshold=2)
        next_tx_subfulfillment1 = cc.Ed25519Fulfillment(public_key=other1_vk)
        next_tx_subfulfillment1.sign(next_tx_fulfillment_message, crypto.SigningKey(other1_sk))
        next_tx_fulfillment.add_subfulfillment(next_tx_subfulfillment1)
        next_tx_subfulfillment2 = cc.Ed25519Fulfillment(public_key=other2_vk)
        next_tx_subfulfillment2.sign(next_tx_fulfillment_message, crypto.SigningKey(other2_sk))
        next_tx_fulfillment.add_subfulfillment(next_tx_subfulfillment2)
        # need to add remaining (unsigned) fulfillment as a condition
        next_tx_subfulfillment3 = cc.Ed25519Fulfillment(public_key=other3_vk)
        next_tx_fulfillment.add_subcondition(next_tx_subfulfillment3.condition)
        next_tx['transaction']['fulfillments'][0]['fulfillment'] = next_tx_fulfillment.serialize_uri()

        assert b.validate_transaction(next_tx) == next_tx
        assert b.is_valid_transaction(next_tx) == next_tx

    @pytest.mark.usefixtures('inputs')
    def test_override_condition_and_fulfillment_transfer_threshold_from_json(self, b, user_vk, user_sk):
        other1_sk, other1_vk = crypto.generate_key_pair()
        other2_sk, other2_vk = crypto.generate_key_pair()
        other3_sk, other3_vk = crypto.generate_key_pair()

        first_input_tx = b.get_owned_ids(user_vk).pop()
        first_tx = b.create_transaction(user_vk, [other1_vk, other2_vk, other3_vk], first_input_tx, 'TRANSFER')

        first_tx_condition = cc.ThresholdSha256Fulfillment(threshold=2)
        first_tx_condition.add_subfulfillment(cc.Ed25519Fulfillment(public_key=other1_vk))
        first_tx_condition.add_subfulfillment(cc.Ed25519Fulfillment(public_key=other2_vk))
        first_tx_condition.add_subfulfillment(cc.Ed25519Fulfillment(public_key=other3_vk))

        first_tx['transaction']['conditions'][0]['condition'] = {
            'details': json.loads(first_tx_condition.serialize_json()),
            'uri': first_tx_condition.condition.serialize_uri()
        }
        # conditions have been updated, so hash needs updating
        first_tx['id'] = util.get_hash_data(first_tx)

        first_tx_signed = b.sign_transaction(first_tx, user_sk)

        assert b.validate_transaction(first_tx_signed) == first_tx_signed
        assert b.is_valid_transaction(first_tx_signed) == first_tx_signed

        b.write_transaction(first_tx_signed)

        # create and write block to bigchain
        block = b.create_block([first_tx])
        b.write_block(block, durability='hard')

        next_input_tx = b.get_owned_ids(other1_vk).pop()
        # create another transaction with the same input
        next_tx = b.create_transaction([other1_vk, other2_vk, other3_vk], user_vk, next_input_tx, 'TRANSFER')

        next_tx_fulfillment = next_tx['transaction']['fulfillments'][0]
        next_tx_fulfillment_message = util.get_fulfillment_message(next_tx, next_tx_fulfillment, serialized=True)

        # parse the threshold cryptocondition
        next_tx_fulfillment = cc.Fulfillment.from_json(first_tx['transaction']['conditions'][0]['condition']['details'])

        subfulfillment1 = next_tx_fulfillment.get_subcondition_from_vk(other1_vk)[0]
        subfulfillment2 = next_tx_fulfillment.get_subcondition_from_vk(other2_vk)[0]
        subfulfillment3 = next_tx_fulfillment.get_subcondition_from_vk(other3_vk)[0]

        next_tx_fulfillment.subconditions = []
        # sign the subconditions until threshold of 2 is reached
        subfulfillment1.sign(next_tx_fulfillment_message, crypto.SigningKey(other1_sk))
        next_tx_fulfillment.add_subfulfillment(subfulfillment1)
        subfulfillment2.sign(next_tx_fulfillment_message, crypto.SigningKey(other2_sk))
        next_tx_fulfillment.add_subfulfillment(subfulfillment2)
        next_tx_fulfillment.add_subcondition(subfulfillment3.condition)

        next_tx['transaction']['fulfillments'][0]['fulfillment'] = next_tx_fulfillment.serialize_uri()
        assert b.validate_transaction(next_tx) == next_tx
        assert b.is_valid_transaction(next_tx) == next_tx

    @pytest.mark.usefixtures('inputs')
    def test_override_condition_and_fulfillment_transfer_threshold_wrongly_signed(self, b, user_vk, user_sk):
        other1_sk, other1_vk = crypto.generate_key_pair()
        other2_sk, other2_vk = crypto.generate_key_pair()

        first_input_tx = b.get_owned_ids(user_vk).pop()
        first_tx = b.create_transaction(user_vk, [other1_vk, other2_vk], first_input_tx, 'TRANSFER')

        first_tx_condition = cc.ThresholdSha256Fulfillment(threshold=2)
        first_tx_condition.add_subfulfillment(cc.Ed25519Fulfillment(public_key=other1_vk))
        first_tx_condition.add_subfulfillment(cc.Ed25519Fulfillment(public_key=other2_vk))

        first_tx['transaction']['conditions'][0]['condition'] = {
            'details': json.loads(first_tx_condition.serialize_json()),
            'uri': first_tx_condition.condition.serialize_uri()
        }
        # conditions have been updated, so hash needs updating
        first_tx['id'] = util.get_hash_data(first_tx)

        first_tx_signed = b.sign_transaction(first_tx, user_sk)

        assert b.validate_transaction(first_tx_signed) == first_tx_signed
        assert b.is_valid_transaction(first_tx_signed) == first_tx_signed

        b.write_transaction(first_tx_signed)

        # create and write block to bigchain
        block = b.create_block([first_tx])
        b.write_block(block, durability='hard')

        next_input_tx = b.get_owned_ids(other1_vk).pop()
        # create another transaction with the same input
        next_tx = b.create_transaction([other1_vk, other2_vk], user_vk, next_input_tx, 'TRANSFER')

        next_tx_fulfillment = next_tx['transaction']['fulfillments'][0]
        next_tx_fulfillment_message = util.get_fulfillment_message(next_tx, next_tx_fulfillment, serialized=True)
        next_tx_fulfillment = cc.ThresholdSha256Fulfillment(threshold=2)
        next_tx_subfulfillment1 = cc.Ed25519Fulfillment(public_key=other1_vk)
        next_tx_subfulfillment1.sign(next_tx_fulfillment_message, crypto.SigningKey(other1_sk))
        next_tx_fulfillment.add_subfulfillment(next_tx_subfulfillment1)

        # Wrong signing happens here
        next_tx_subfulfillment2 = cc.Ed25519Fulfillment(public_key=other1_vk)
        next_tx_subfulfillment2.sign(next_tx_fulfillment_message, crypto.SigningKey(other1_sk))
        next_tx_fulfillment.add_subfulfillment(next_tx_subfulfillment2)
        next_tx['transaction']['fulfillments'][0]['fulfillment'] = next_tx_fulfillment.serialize_uri()

        with pytest.raises(exceptions.InvalidSignature):
            b.validate_transaction(next_tx)
        assert b.is_valid_transaction(next_tx) == False

    def test_default_threshold_conditions_for_multiple_owners(self, b, user_sk, user_vk):
        user2_sk, user2_vk = crypto.generate_key_pair()

        # create transaction with multiple new_owners
        tx = b.create_transaction(b.me, [user_vk, user2_vk], None, 'CREATE')

        assert len(tx['transaction']['conditions']) == 1
        assert len(tx['transaction']['conditions'][0]['condition']['details']['subfulfillments']) == 2

        # expected condition subfulfillments
        expected_condition = cc.ThresholdSha256Fulfillment(threshold=2)
        expected_condition.add_subfulfillment(cc.Ed25519Fulfillment(public_key=user_vk))
        expected_condition.add_subfulfillment(cc.Ed25519Fulfillment(public_key=user2_vk))
        tx_expected_condition = {
            'details': json.loads(expected_condition.serialize_json()),
            'uri': expected_condition.condition.serialize_uri()
        }

        assert tx['transaction']['conditions'][0]['condition'] == tx_expected_condition

    def test_default_threshold_fulfillments_for_multiple_owners(self, b, user_sk, user_vk):
        user2_sk, user2_vk = crypto.generate_key_pair()

        # create transaction with multiple new_owners
        tx_create = b.create_transaction(b.me, [user_vk, user2_vk], None, 'CREATE')
        tx_create_signed = b.sign_transaction(tx_create, b.me_private)
        block = b.create_block([tx_create_signed])
        b.write_block(block, durability='hard')

        inputs = b.get_owned_ids(user_vk)

        # create a transaction with multiple current owners
        tx_transfer = b.create_transaction([user_vk, user2_vk], b.me, inputs, 'TRANSFER')
        tx_transfer_signed = b.sign_transaction(tx_transfer, [user_sk, user2_sk])

        # expected fulfillment
        expected_fulfillment = cc.Fulfillment.from_json(tx_create['transaction']['conditions'][0]['condition']['details'])
        subfulfillment1 = expected_fulfillment.subconditions[0]['body']
        subfulfillment2 = expected_fulfillment.subconditions[1]['body']

        expected_fulfillment_message = util.get_fulfillment_message(tx_transfer,
                                                                    tx_transfer['transaction']['fulfillments'][0])

        subfulfillment1.sign(util.serialize(expected_fulfillment_message), crypto.SigningKey(user_sk))
        subfulfillment2.sign(util.serialize(expected_fulfillment_message), crypto.SigningKey(user2_sk))

        assert tx_transfer_signed['transaction']['fulfillments'][0]['fulfillment'] \
            == expected_fulfillment.serialize_uri()

        assert b.validate_fulfillments(tx_transfer_signed) is True

    def test_create_asset_with_hashlock_condition(self, b):
        hashlock_tx = b.create_transaction(b.me, None, None, 'CREATE')

        secret = b'much secret! wow!'
        first_tx_condition = cc.PreimageSha256Fulfillment(preimage=secret)

        hashlock_tx['transaction']['conditions'].append({
            'condition': {
                'details': json.loads(first_tx_condition.serialize_json()),
                'uri': first_tx_condition.condition.serialize_uri()
            },
            'cid': 0,
            'new_owners': None
        })
        # conditions have been updated, so hash needs updating
        hashlock_tx['id'] = util.get_hash_data(hashlock_tx)

        hashlock_tx_signed = b.sign_transaction(hashlock_tx, b.me_private)

        assert b.validate_transaction(hashlock_tx_signed) == hashlock_tx_signed
        assert b.is_valid_transaction(hashlock_tx_signed) == hashlock_tx_signed

        b.write_transaction(hashlock_tx_signed)

        # create and write block to bigchain
        block = b.create_block([hashlock_tx_signed])
        b.write_block(block, durability='hard')

    @pytest.mark.usefixtures('inputs')
    def test_transfer_asset_with_hashlock_condition(self, b, user_vk, user_sk):
        first_input_tx = b.get_owned_ids(user_vk).pop()

        hashlock_tx = b.create_transaction(user_vk, None, first_input_tx, 'TRANSFER')

        secret = b'much secret! wow!'
        first_tx_condition = cc.PreimageSha256Fulfillment(preimage=secret)

        hashlock_tx['transaction']['conditions'].append({
            'condition': {
                'details': json.loads(first_tx_condition.serialize_json()),
                'uri': first_tx_condition.condition.serialize_uri()
            },
            'cid': 0,
            'new_owners': None
        })
        # conditions have been updated, so hash needs updating
        hashlock_tx['id'] = util.get_hash_data(hashlock_tx)

        hashlock_tx_signed = b.sign_transaction(hashlock_tx, user_sk)

        assert b.validate_transaction(hashlock_tx_signed) == hashlock_tx_signed
        assert b.is_valid_transaction(hashlock_tx_signed) == hashlock_tx_signed
        assert len(b.get_owned_ids(user_vk)) == 1

        b.write_transaction(hashlock_tx_signed)

        # create and write block to bigchain
        block = b.create_block([hashlock_tx_signed])
        b.write_block(block, durability='hard')

        assert len(b.get_owned_ids(user_vk)) == 0

    def test_create_and_fulfill_asset_with_hashlock_condition(self, b, user_vk):
        hashlock_tx = b.create_transaction(b.me, None, None, 'CREATE')

        secret = b'much secret! wow!'
        first_tx_condition = cc.PreimageSha256Fulfillment(preimage=secret)

        hashlock_tx['transaction']['conditions'].append({
            'condition': {
                'details': json.loads(first_tx_condition.serialize_json()),
                'uri': first_tx_condition.condition.serialize_uri()
            },
            'cid': 0,
            'new_owners': None
        })
        # conditions have been updated, so hash needs updating
        hashlock_tx['id'] = util.get_hash_data(hashlock_tx)

        hashlock_tx_signed = b.sign_transaction(hashlock_tx, b.me_private)

        assert b.validate_transaction(hashlock_tx_signed) == hashlock_tx_signed
        assert b.is_valid_transaction(hashlock_tx_signed) == hashlock_tx_signed

        b.write_transaction(hashlock_tx_signed)

        # create and write block to bigchain
        block = b.create_block([hashlock_tx_signed])
        b.write_block(block, durability='hard')

        assert len(b.get_owned_ids(b.me)) == 0

        # create hashlock fulfillment tx
        hashlock_fulfill_tx = b.create_transaction(None, user_vk, {'txid': hashlock_tx['id'], 'cid': 0}, 'TRANSFER')

        hashlock_fulfill_tx_fulfillment = cc.PreimageSha256Fulfillment(preimage=b'')
        hashlock_fulfill_tx['transaction']['fulfillments'][0]['fulfillment'] = \
            hashlock_fulfill_tx_fulfillment.serialize_uri()

        with pytest.raises(exceptions.InvalidSignature):
            b.validate_transaction(hashlock_fulfill_tx)
        assert b.is_valid_transaction(hashlock_fulfill_tx) == False

        hashlock_fulfill_tx_fulfillment = cc.PreimageSha256Fulfillment(preimage=secret)
        hashlock_fulfill_tx['transaction']['fulfillments'][0]['fulfillment'] = \
            hashlock_fulfill_tx_fulfillment.serialize_uri()

        assert b.validate_transaction(hashlock_fulfill_tx) == hashlock_fulfill_tx
        assert b.is_valid_transaction(hashlock_fulfill_tx) == hashlock_fulfill_tx

        b.write_transaction(hashlock_fulfill_tx)

        # create and write block to bigchain
        block = b.create_block([hashlock_fulfill_tx])
        b.write_block(block, durability='hard')

        assert len(b.get_owned_ids(b.me)) == 0
        assert len(b.get_owned_ids(user_vk)) == 1

        # try doublespending
        user2_sk, user2_vk = crypto.generate_key_pair()
        hashlock_doublespend_tx = b.create_transaction(None, user2_vk, {'txid': hashlock_tx['id'], 'cid': 0}, 'TRANSFER')

        hashlock_doublespend_tx_fulfillment = cc.PreimageSha256Fulfillment(preimage=secret)
        hashlock_doublespend_tx['transaction']['fulfillments'][0]['fulfillment'] = \
            hashlock_doublespend_tx_fulfillment.serialize_uri()

        with pytest.raises(exceptions.DoubleSpend):
            b.validate_transaction(hashlock_doublespend_tx)

    def test_get_subcondition_from_vk(self, b, user_sk, user_vk):
        user2_sk, user2_vk = crypto.generate_key_pair()
        user3_sk, user3_vk = crypto.generate_key_pair()
        user4_sk, user4_vk = crypto.generate_key_pair()
        user5_sk, user5_vk = crypto.generate_key_pair()
        new_owners = [user_vk, user2_vk, user3_vk, user4_vk, user5_vk]

        # create a transaction with multiple new_owners
        tx = b.create_transaction(b.me, new_owners, None, 'CREATE')
        condition = cc.Fulfillment.from_json(tx['transaction']['conditions'][0]['condition']['details'])

        for new_owner in new_owners:
            subcondition = condition.get_subcondition_from_vk(new_owner)[0]
            assert subcondition.public_key.to_ascii().decode() == new_owner
