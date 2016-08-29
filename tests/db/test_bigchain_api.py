import copy
import time

import pytest
import rethinkdb as r
import cryptoconditions as cc

import bigchaindb
from bigchaindb import crypto, exceptions, util


@pytest.mark.skipif(reason='Some tests throw a ResourceWarning that might result in some weird '
                           'exceptions while running the tests. The problem seems to *not* '
                           'interfere with the correctness of the tests. ')
def test_remove_unclosed_sockets():
    pass


# Some util functions
def dummy_tx():
    b = bigchaindb.Bigchain()
    tx = b.create_transaction(b.me, b.me, None, 'CREATE')
    tx_signed = b.sign_transaction(tx, b.me_private)
    return tx_signed


def dummy_block():
    b = bigchaindb.Bigchain()
    block = b.create_block([dummy_tx()])
    return block


class TestBigchainApi(object):
    def test_create_transaction_create(self, b, user_sk):
        tx = b.create_transaction(b.me, user_sk, None, 'CREATE')

        assert sorted(tx) == ['id', 'transaction']
        assert sorted(tx['transaction']) == ['conditions', 'data', 'fulfillments', 'operation', 'timestamp', 'version']

    def test_create_transaction_with_unsupported_payload_raises(self, b):
        with pytest.raises(TypeError):
            b.create_transaction('a', 'b', 'c', 'd', payload=[])

    def test_create_transaction_payload_none(self, b, user_vk):
        tx = b.create_transaction(b.me, user_vk, None, 'CREATE')
        assert len(tx['transaction']['data']['uuid']) == 36
        assert tx['transaction']['data']['payload'] is None

    def test_create_transaction_payload(self, b, user_vk):
        payload = {'msg': 'Hello BigchainDB!'}
        tx = b.create_transaction(b.me, user_vk, None, 'CREATE', payload=payload)
        assert len(tx['transaction']['data']['uuid']) == 36
        assert tx['transaction']['data']['payload'] == payload

    def test_get_transactions_for_payload(self, b, user_vk):
        payload = {'msg': 'Hello BigchainDB!'}
        tx = b.create_transaction(b.me, user_vk, None, 'CREATE', payload=payload)
        payload_uuid = tx['transaction']['data']['uuid']

        block = b.create_block([tx])
        b.write_block(block, durability='hard')

        matches = b.get_tx_by_payload_uuid(payload_uuid)
        assert len(matches) == 1
        assert matches[0]['id'] == tx['id']

    def test_get_transactions_for_payload_mismatch(self, b, user_vk):
        matches = b.get_tx_by_payload_uuid('missing')
        assert not matches

    @pytest.mark.usefixtures('inputs')
    def test_create_transaction_transfer(self, b, user_vk, user_sk):
        input_tx = b.get_owned_ids(user_vk).pop()
        assert b.validate_fulfillments(b.get_transaction(input_tx['txid'])) == True

        tx = b.create_transaction(user_vk, b.me, input_tx, 'TRANSFER')

        assert sorted(tx) == ['id', 'transaction']
        assert sorted(tx['transaction']) == ['conditions', 'data', 'fulfillments', 'operation', 'timestamp', 'version']

        tx_signed = b.sign_transaction(tx, user_sk)

        assert b.validate_fulfillments(tx) == False
        assert b.validate_fulfillments(tx_signed) == True

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
    def test_read_transaction_undecided_block(self, b, user_vk, user_sk):
        input_tx = b.get_owned_ids(user_vk).pop()
        tx = b.create_transaction(user_vk, user_vk, input_tx, 'TRANSFER')
        tx_signed = b.sign_transaction(tx, user_sk)

        # create block and write it to the bighcain before retrieving the transaction
        block = b.create_block([tx_signed])
        b.write_block(block, durability='hard')

        response, status = b.get_transaction(tx_signed["id"], include_status=True)
        # add validity information, which will be returned
        assert util.serialize(tx_signed) == util.serialize(response)
        assert status == b.TX_UNDECIDED

    @pytest.mark.usefixtures('inputs')
    def test_read_transaction_backlog(self, b, user_vk, user_sk):
        input_tx = b.get_owned_ids(user_vk).pop()
        tx = b.create_transaction(user_vk, user_vk, input_tx, 'TRANSFER')
        tx_signed = b.sign_transaction(tx, user_sk)
        b.write_transaction(tx_signed)

        response, status = b.get_transaction(tx_signed["id"], include_status=True)
        response.pop('assignee')
        # add validity information, which will be returned
        assert util.serialize(tx_signed) == util.serialize(response)
        assert status == b.TX_IN_BACKLOG

    @pytest.mark.usefixtures('inputs')
    def test_read_transaction_invalid_block(self, b, user_vk, user_sk):
        input_tx = b.get_owned_ids(user_vk).pop()
        tx = b.create_transaction(user_vk, user_vk, input_tx, 'TRANSFER')
        tx_signed = b.sign_transaction(tx, user_sk)

        # create block
        block = b.create_block([tx_signed])
        b.write_block(block, durability='hard')

        # vote the block invalid
        vote = b.vote(block['id'], b.get_last_voted_block()['id'], False)
        b.write_vote(vote)
        response = b.get_transaction(tx_signed["id"])

        # should be None, because invalid blocks are ignored
        assert response is None

    @pytest.mark.usefixtures('inputs')
    def test_read_transaction_valid_block(self, b, user_vk, user_sk):
        input_tx = b.get_owned_ids(user_vk).pop()
        tx = b.create_transaction(user_vk, user_vk, input_tx, 'TRANSFER')
        tx_signed = b.sign_transaction(tx, user_sk)
        b.write_transaction(tx_signed)

        # create block
        block = b.create_block([tx_signed])
        b.write_block(block, durability='hard')

        # vote the block invalid
        vote = b.vote(block['id'], b.get_last_voted_block()['id'], True)
        b.write_vote(vote)

        response, status = b.get_transaction(tx_signed["id"], include_status=True)
        # add validity information, which will be returned
        assert util.serialize(tx_signed) == util.serialize(response)
        assert status == b.TX_VALID

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
            b.nodes_except_me.append(crypto.generate_key_pair()[1])

        # test assignee for several transactions
        for _ in range(20):
            input_tx = b.get_owned_ids(user_vk).pop()
            tx = b.create_transaction(user_vk, user_vk, input_tx, 'TRANSFER')
            tx_signed = b.sign_transaction(tx, user_sk)
            b.write_transaction(tx_signed)

            # retrieve the transaction
            response = r.table('backlog').get(tx_signed['id']).run(b.conn)

            # check if the assignee is one of the _other_ federation nodes
            assert response['assignee'] in b.nodes_except_me

    @pytest.mark.usefixtures('inputs')
    def test_genesis_block(self, b):
        response = list(r.table('bigchain')
                        .filter(util.is_genesis_block)
                        .run(b.conn))

        assert len(response) == 1
        block = response[0]
        assert len(block['block']['transactions']) == 1
        assert block['block']['transactions'][0]['transaction']['operation'] == 'GENESIS'
        assert block['block']['transactions'][0]['transaction']['fulfillments'][0]['input'] is None

    def test_create_genesis_block_fails_if_table_not_empty(self, b):
        b.create_genesis_block()

        with pytest.raises(exceptions.GenesisBlockAlreadyExistsError):
            b.create_genesis_block()

        genesis_blocks = list(r.table('bigchain')
                              .filter(util.is_genesis_block)
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
        tx = dummy_tx()
        new_block = b.create_block([tx])
        block_hash = crypto.hash_data(util.serialize(new_block['block']))

        assert new_block['block']['voters'] == [b.me]
        assert new_block['block']['node_pubkey'] == b.me
        assert crypto.VerifyingKey(b.me).verify(util.serialize(new_block['block']), new_block['signature']) is True
        assert new_block['id'] == block_hash

    def test_create_empty_block(self, b):
        with pytest.raises(exceptions.OperationError) as excinfo:
            b.create_block([])

        assert excinfo.value.args[0] == 'Empty block creation is not allowed'

    def test_get_last_voted_block_returns_genesis_if_no_votes_has_been_casted(self, b):
        b.create_genesis_block()
        genesis = list(r.table('bigchain')
                       .filter(util.is_genesis_block)
                       .run(b.conn))[0]
        gb = b.get_last_voted_block()
        assert gb == genesis
        assert b.validate_block(gb) == gb

    def test_get_last_voted_block_returns_the_correct_block_same_timestamp(self, b, monkeypatch):
        genesis = b.create_genesis_block()

        assert b.get_last_voted_block() == genesis

        block_1 = dummy_block()
        block_2 = dummy_block()
        block_3 = dummy_block()

        b.write_block(block_1, durability='hard')
        b.write_block(block_2, durability='hard')
        b.write_block(block_3, durability='hard')

        # make sure all the blocks are written at the same time
        monkeypatch.setattr(util, 'timestamp', lambda: '1')

        b.write_vote(b.vote(block_1['id'], b.get_last_voted_block()['id'], True))
        assert b.get_last_voted_block()['id'] == block_1['id']

        b.write_vote(b.vote(block_2['id'], b.get_last_voted_block()['id'], True))
        assert b.get_last_voted_block()['id'] == block_2['id']

        b.write_vote(b.vote(block_3['id'], b.get_last_voted_block()['id'], True))
        assert b.get_last_voted_block()['id'] == block_3['id']


    def test_get_last_voted_block_returns_the_correct_block_different_timestamps(self, b, monkeypatch):
        genesis = b.create_genesis_block()

        assert b.get_last_voted_block() == genesis

        block_1 = dummy_block()
        block_2 = dummy_block()
        block_3 = dummy_block()

        b.write_block(block_1, durability='hard')
        b.write_block(block_2, durability='hard')
        b.write_block(block_3, durability='hard')

        # make sure all the blocks are written at different timestamps
        monkeypatch.setattr(util, 'timestamp', lambda: '1')
        b.write_vote(b.vote(block_1['id'], b.get_last_voted_block()['id'], True))
        assert b.get_last_voted_block()['id'] == block_1['id']

        monkeypatch.setattr(util, 'timestamp', lambda: '2')
        b.write_vote(b.vote(block_2['id'], b.get_last_voted_block()['id'], True))
        assert b.get_last_voted_block()['id'] == block_2['id']

        monkeypatch.setattr(util, 'timestamp', lambda: '3')
        b.write_vote(b.vote(block_3['id'], b.get_last_voted_block()['id'], True))
        assert b.get_last_voted_block()['id'] == block_3['id']

    def test_no_vote_written_if_block_already_has_vote(self, b):
        genesis = b.create_genesis_block()

        block_1 = dummy_block()

        b.write_block(block_1, durability='hard')

        b.write_vote(b.vote(block_1['id'], genesis['id'], True))
        retrieved_block_1 = r.table('bigchain').get(block_1['id']).run(b.conn)

        # try to vote again on the retrieved block, should do nothing
        b.write_vote(b.vote(retrieved_block_1['id'], genesis['id'], True))
        retrieved_block_2 = r.table('bigchain').get(block_1['id']).run(b.conn)

        assert retrieved_block_1 == retrieved_block_2

    def test_more_votes_than_voters(self, b):
        b.create_genesis_block()
        block_1 = dummy_block()
        b.write_block(block_1, durability='hard')
        # insert duplicate votes
        vote_1 = b.vote(block_1['id'], b.get_last_voted_block()['id'], True)
        vote_2 = b.vote(block_1['id'], b.get_last_voted_block()['id'], True)
        vote_2['node_pubkey'] = 'aaaaaaa'
        r.table('votes').insert(vote_1).run(b.conn)
        r.table('votes').insert(vote_2).run(b.conn)

        from bigchaindb.exceptions import MultipleVotesError
        with pytest.raises(MultipleVotesError) as excinfo:
            b.block_election_status(block_1)
        assert excinfo.value.args[0] == 'Block {block_id} has {n_votes} votes cast, but only {n_voters} voters'\
            .format(block_id=block_1['id'], n_votes=str(2), n_voters=str(1))

    def test_multiple_votes_single_node(self, b):
        genesis = b.create_genesis_block()
        block_1 = dummy_block()
        b.write_block(block_1, durability='hard')
        # insert duplicate votes
        for i in range(2):
            r.table('votes').insert(b.vote(block_1['id'], genesis['id'], True)).run(b.conn)

        from bigchaindb.exceptions import MultipleVotesError
        with pytest.raises(MultipleVotesError) as excinfo:
            b.block_election_status(block_1)
        assert excinfo.value.args[0] == 'Block {block_id} has multiple votes ({n_votes}) from voting node {node_id}'\
            .format(block_id=block_1['id'], n_votes=str(2), node_id=b.me)

        with pytest.raises(MultipleVotesError) as excinfo:
            b.has_previous_vote(block_1)
        assert excinfo.value.args[0] == 'Block {block_id} has {n_votes} votes from public key {me}'\
            .format(block_id=block_1['id'], n_votes=str(2), me=b.me)

    def test_improper_vote_error(selfs, b):
        b.create_genesis_block()
        block_1 = dummy_block()
        b.write_block(block_1, durability='hard')
        vote_1 = b.vote(block_1['id'], b.get_last_voted_block()['id'], True)
        # mangle the signature
        vote_1['signature'] = 'a' * 87
        r.table('votes').insert(vote_1).run(b.conn)
        from bigchaindb.exceptions import ImproperVoteError
        with pytest.raises(ImproperVoteError) as excinfo:
            b.has_previous_vote(block_1)
        assert excinfo.value.args[0] == 'Block {block_id} already has an incorrectly signed ' \
                                  'vote from public key {me}'.format(block_id=block_1['id'], me=b.me)


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

        # assert excinfo.value.args[0] == 'owner_before `a` does not own the input `{}`'.format(valid_input)
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
        block = dummy_block()

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
            'voters': b.nodes_except_me
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

        assert excinfo.value.args[0] == 'owner_before `a` does not own the input `{}`'.format(valid_input)

    def test_invalid_block_id(self, b):
        block = dummy_block()

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
        block = dummy_block()

        # replace the block signature with an invalid one
        block['signature'] = crypto.SigningKey(b.me_private).sign(b'wrongdata')

        # check that validate_block raises an InvalidSignature exception
        with pytest.raises(exceptions.InvalidSignature):
            b.validate_block(block)

    def test_invalid_node_pubkey(self, b):
        # blocks can only be created by a federation node
        # create a valid block
        block = dummy_block()

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

    def test_single_owner_before_multiple_owners_after_single_input(self, b, user_sk, user_vk, inputs):
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

    def test_single_owner_before_multiple_owners_after_multiple_inputs(self, b, user_sk, user_vk):
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

    def test_multiple_owners_before_single_owner_after_single_input(self, b, user_sk, user_vk):
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

    def test_multiple_owners_before_single_owner_after_multiple_inputs(self, b, user_sk, user_vk):
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

    def test_multiple_owners_before_multiple_owners_after_single_input(self, b, user_sk, user_vk):
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

    def test_multiple_owners_before_multiple_owners_after_multiple_inputs(self, b, user_sk, user_vk):
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

    def test_get_owned_ids_single_tx_single_output_invalid_block(self, b, user_sk, user_vk):
        genesis = b.create_genesis_block()
        # create a new users
        user2_sk, user2_vk = crypto.generate_key_pair()

        # create input to spend
        tx = b.create_transaction(b.me, user_vk, None, 'CREATE')
        tx_signed = b.sign_transaction(tx, b.me_private)
        block = b.create_block([tx_signed])
        b.write_block(block, durability='hard')

        # vote the block VALID
        vote = b.vote(block['id'], genesis['id'], True)
        b.write_vote(vote)

        # get input
        owned_inputs_user1 = b.get_owned_ids(user_vk)
        owned_inputs_user2 = b.get_owned_ids(user2_vk)
        assert owned_inputs_user1 == [{'cid': 0, 'txid': tx['id']}]
        assert owned_inputs_user2 == []

        # create a transaction and block
        tx_invalid = b.create_transaction(user_vk, user2_vk, owned_inputs_user1, 'TRANSFER')
        tx_invalid_signed = b.sign_transaction(tx_invalid, user_sk)
        block = b.create_block([tx_invalid_signed])
        b.write_block(block, durability='hard')

        # vote the block invalid
        vote = b.vote(block['id'], b.get_last_voted_block()['id'], False)
        b.write_vote(vote)

        owned_inputs_user1 = b.get_owned_ids(user_vk)
        owned_inputs_user2 = b.get_owned_ids(user2_vk)

        # should be the same as before (note tx, not tx_invalid)
        assert owned_inputs_user1 == [{'cid': 0, 'txid': tx['id']}]
        assert owned_inputs_user2 == []

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

    def test_get_spent_single_tx_single_output_invalid_block(self, b, user_sk, user_vk):
        genesis = b.create_genesis_block()

        # create a new users
        user2_sk, user2_vk = crypto.generate_key_pair()

        # create input to spend
        tx = b.create_transaction(b.me, user_vk, None, 'CREATE')
        tx_signed = b.sign_transaction(tx, b.me_private)
        block = b.create_block([tx_signed])
        b.write_block(block, durability='hard')

        # vote the block VALID
        vote = b.vote(block['id'], genesis['id'], True)
        b.write_vote(vote)

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

        # vote the block invalid
        vote = b.vote(block['id'], b.get_last_voted_block()['id'], False)
        b.write_vote(vote)
        response = b.get_transaction(tx_signed["id"])
        spent_inputs_user1 = b.get_spent(owned_inputs_user1[0])

        # Now there should be no spents (the block is invalid)
        assert spent_inputs_user1 is None

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


class TestFulfillmentMessage(object):
    def test_fulfillment_message_create(self, b, user_vk):
        tx = b.create_transaction(b.me, user_vk, None, 'CREATE', payload={'pay': 'load'})
        original_fulfillment = tx['transaction']['fulfillments'][0]
        fulfillment_message = util.get_fulfillment_message(tx, original_fulfillment)

        assert sorted(fulfillment_message) == \
               ['condition', 'data', 'fulfillment', 'id', 'operation', 'timestamp', 'version']

        assert fulfillment_message['data']['payload'] == tx['transaction']['data']['payload']
        assert fulfillment_message['id'] == tx['id']
        assert fulfillment_message['condition'] == tx['transaction']['conditions'][0]
        assert fulfillment_message['fulfillment']['owners_before'] == original_fulfillment['owners_before']
        assert fulfillment_message['fulfillment']['fid'] == original_fulfillment['fid']
        assert fulfillment_message['fulfillment']['input'] == original_fulfillment['input']
        assert fulfillment_message['operation'] == tx['transaction']['operation']
        assert fulfillment_message['timestamp'] == tx['transaction']['timestamp']
        assert fulfillment_message['version'] == tx['transaction']['version']

    @pytest.mark.usefixtures('inputs')
    def test_fulfillment_message_transfer(self, b, user_vk):
        input_tx = b.get_owned_ids(user_vk).pop()
        assert b.validate_fulfillments(b.get_transaction(input_tx['txid'])) == True

        tx = b.create_transaction(user_vk, b.me, input_tx, 'TRANSFER', payload={'pay': 'load'})

        original_fulfillment = tx['transaction']['fulfillments'][0]
        fulfillment_message = util.get_fulfillment_message(tx, original_fulfillment)

        assert sorted(fulfillment_message) == \
               ['condition', 'data', 'fulfillment', 'id', 'operation', 'timestamp', 'version']

        assert fulfillment_message['data']['payload'] == tx['transaction']['data']['payload']
        assert fulfillment_message['id'] == tx['id']
        assert fulfillment_message['condition'] == tx['transaction']['conditions'][0]
        assert fulfillment_message['fulfillment']['owners_before'] == original_fulfillment['owners_before']
        assert fulfillment_message['fulfillment']['fid'] == original_fulfillment['fid']
        assert fulfillment_message['fulfillment']['input'] == original_fulfillment['input']
        assert fulfillment_message['operation'] == tx['transaction']['operation']
        assert fulfillment_message['timestamp'] == tx['transaction']['timestamp']
        assert fulfillment_message['version'] == tx['transaction']['version']

    def test_fulfillment_message_multiple_owners_before_multiple_owners_after_multiple_inputs(self, b, user_vk):
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
        tx = b.create_transaction([user_vk, user2_vk], [user3_vk, user4_vk], inp, 'TRANSFER', payload={'pay': 'load'})

        for original_fulfillment in tx['transaction']['fulfillments']:
            fulfillment_message = util.get_fulfillment_message(tx, original_fulfillment)

            assert sorted(fulfillment_message) == \
                   ['condition', 'data', 'fulfillment', 'id', 'operation', 'timestamp', 'version']

            assert fulfillment_message['data']['payload'] == tx['transaction']['data']['payload']
            assert fulfillment_message['id'] == tx['id']
            assert fulfillment_message['condition'] == tx['transaction']['conditions'][original_fulfillment['fid']]
            assert fulfillment_message['fulfillment']['owners_before'] == original_fulfillment['owners_before']
            assert fulfillment_message['fulfillment']['fid'] == original_fulfillment['fid']
            assert fulfillment_message['fulfillment']['input'] == original_fulfillment['input']
            assert fulfillment_message['operation'] == tx['transaction']['operation']
            assert fulfillment_message['timestamp'] == tx['transaction']['timestamp']
            assert fulfillment_message['version'] == tx['transaction']['version']


class TestTransactionMalleability(object):
    @pytest.mark.usefixtures('inputs')
    def test_create_transaction_transfer(self, b, user_vk, user_sk):
        input_tx = b.get_owned_ids(user_vk).pop()
        assert b.validate_fulfillments(b.get_transaction(input_tx['txid'])) is True

        tx = b.create_transaction(user_vk, b.me, input_tx, 'TRANSFER')

        tx_signed = b.sign_transaction(tx, user_sk)

        assert b.validate_fulfillments(tx_signed) is True
        assert b.is_valid_transaction(tx_signed) == tx_signed

        tx_changed = copy.deepcopy(tx_signed)
        tx_changed['id'] = 'dsdasd'
        assert b.validate_fulfillments(tx_changed) is False
        assert b.is_valid_transaction(tx_changed) is False

        tx_changed = copy.deepcopy(tx_signed)
        tx_changed['transaction']['version'] = '0'
        assert b.validate_fulfillments(tx_changed) is False
        assert b.is_valid_transaction(tx_changed) is False

        tx_changed = copy.deepcopy(tx_signed)
        tx_changed['transaction']['operation'] = 'CREATE'
        assert b.validate_fulfillments(tx_changed) is False
        assert b.is_valid_transaction(tx_changed) is False

        tx_changed = copy.deepcopy(tx_signed)
        tx_changed['transaction']['timestamp'] = '1463033192.123456'
        assert b.validate_fulfillments(tx_changed) is False
        assert b.is_valid_transaction(tx_changed) is False

        tx_changed = copy.deepcopy(tx_signed)
        tx_changed['transaction']['data'] = {
            "hash": "872fa6e6f46246cd44afdb2ee9cfae0e72885fb0910e2bcf9a5a2a4eadb417b8",
            "payload": {
                "msg": "Hello BigchainDB!"
            }
        }
        assert b.validate_fulfillments(tx_changed) == False

        tx_changed = copy.deepcopy(tx_signed)
        tx_changed['transaction']['fulfillments'] = [
            {
                "owners_before": [
                    "AFbofwJYEB7Cx2fgrPrCJzbdDVRzRKysoGXt4DsvuTGN"
                ],
                "fid": 0,
                "fulfillment": "cf:4:iXaq3UbandDj4DgBhFDcfHjkm2639RwgLmwAHUmuDFMfMEKMZ71eQw2qCMK951kBaNNJel_FCDuYnacn_MsWzYXOUJs6DGW3lYfXI_d55xuqpH2BenvRWKNp98tRRr4B",
                "input": None
            }
        ]
        assert b.validate_fulfillments(tx_changed) is False
        assert b.is_valid_transaction(tx_changed) is False

        tx_changed = copy.deepcopy(tx_signed)
        tx_changed['transaction']['fulfillments'][0]['fid'] = 1
        with pytest.raises(IndexError):
            assert b.validate_fulfillments(tx_changed) is False
        assert b.is_valid_transaction(tx_changed) is False

        tx_changed = copy.deepcopy(tx_signed)
        tx_changed['transaction']['fulfillments'][0]['owners_before'] = [
            "AFbofwJYEB7Cx2fgrPrCJzbdDVRzRKysoGXt4DsvuTGN"]
        assert b.validate_fulfillments(tx_changed) is False
        assert b.is_valid_transaction(tx_changed) is False

        tx_changed = copy.deepcopy(tx_signed)
        tx_changed['transaction']['fulfillments'][0]['input'] = {
            "cid": 0,
            "txid": "3055348675fc6f23b75f13c55db6d112b66eee068e99d30a802883d3b1784203"
        }
        with pytest.raises(TypeError):
            assert b.validate_fulfillments(tx_changed) is False
        assert b.is_valid_transaction(tx_changed) is False


class TestCryptoconditions(object):
    def test_fulfillment_transaction_create(self, b, user_vk):
        tx = b.create_transaction(b.me, user_vk, None, 'CREATE')
        condition = tx['transaction']['conditions'][0]['condition']
        condition_from_uri = cc.Condition.from_uri(condition['uri'])
        condition_from_dict = cc.Fulfillment.from_dict(condition['details']).condition

        assert condition_from_uri.serialize_uri() == condition_from_dict.serialize_uri()
        assert condition['details']['public_key'] == user_vk

        tx_signed = b.sign_transaction(tx, b.me_private)
        fulfillment = tx_signed['transaction']['fulfillments'][0]
        fulfillment_from_uri = cc.Fulfillment.from_uri(fulfillment['fulfillment'])

        assert fulfillment['owners_before'][0] == b.me
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
        prev_condition_from_dict = cc.Fulfillment.from_dict(prev_condition['details']).condition

        assert prev_condition_from_uri.serialize_uri() == prev_condition_from_dict.serialize_uri()
        assert prev_condition['details']['public_key'] == user_vk

        condition = tx['transaction']['conditions'][0]['condition']
        condition_from_uri = cc.Condition.from_uri(condition['uri'])
        condition_from_dict = cc.Fulfillment.from_dict(condition['details']).condition

        assert condition_from_uri.serialize_uri() == condition_from_dict.serialize_uri()
        assert condition['details']['public_key'] == other_vk

        tx_signed = b.sign_transaction(tx, user_sk)
        fulfillment = tx_signed['transaction']['fulfillments'][0]
        fulfillment_from_uri = cc.Fulfillment.from_uri(fulfillment['fulfillment'])

        assert fulfillment['owners_before'][0] == user_vk
        assert fulfillment_from_uri.public_key.to_ascii().decode() == user_vk
        assert fulfillment_from_uri.condition.serialize_uri() == prev_condition['uri']
        assert b.validate_fulfillments(tx_signed) == True
        assert b.is_valid_transaction(tx_signed) == tx_signed

    def test_override_condition_create(self, b, user_vk):
        tx = b.create_transaction(b.me, user_vk, None, 'CREATE')
        fulfillment = cc.Ed25519Fulfillment(public_key=user_vk)
        tx['transaction']['conditions'][0]['condition'] = {
            'details': fulfillment.to_dict(),
            'uri': fulfillment.condition.serialize_uri()
        }

        tx_signed = b.sign_transaction(tx, b.me_private)

        fulfillment = tx_signed['transaction']['fulfillments'][0]
        fulfillment_from_uri = cc.Fulfillment.from_uri(fulfillment['fulfillment'])

        assert fulfillment['owners_before'][0] == b.me
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
            'details': fulfillment.to_dict(),
            'uri': fulfillment.condition.serialize_uri()
        }

        tx_signed = b.sign_transaction(tx, user_sk)
        fulfillment = tx_signed['transaction']['fulfillments'][0]
        fulfillment_from_uri = cc.Fulfillment.from_uri(fulfillment['fulfillment'])

        assert fulfillment['owners_before'][0] == user_vk
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
    def test_override_fulfillment_transfer(self, b, user_vk, user_sk):
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
    def test_override_condition_and_fulfillment_transfer(self, b, user_vk, user_sk):
        other_sk, other_vk = crypto.generate_key_pair()
        first_input_tx = b.get_owned_ids(user_vk).pop()
        first_tx = b.create_transaction(user_vk, other_vk, first_input_tx, 'TRANSFER')

        first_tx_condition = cc.Ed25519Fulfillment(public_key=other_vk)
        first_tx['transaction']['conditions'][0]['condition'] = {
            'details': first_tx_condition.to_dict(),
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
            'details': first_tx_condition.to_dict(),
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
    def test_override_condition_and_fulfillment_transfer_threshold_from_dict(self, b, user_vk, user_sk):
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
            'details': first_tx_condition.to_dict(),
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
        next_tx_fulfillment = cc.Fulfillment.from_dict(first_tx['transaction']['conditions'][0]['condition']['details'])

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
            'details': first_tx_condition.to_dict(),
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

        # create transaction with multiple owners_after
        tx = b.create_transaction(b.me, [user_vk, user2_vk], None, 'CREATE')

        assert len(tx['transaction']['conditions']) == 1
        assert len(tx['transaction']['conditions'][0]['condition']['details']['subfulfillments']) == 2

        # expected condition subfulfillments
        expected_condition = cc.ThresholdSha256Fulfillment(threshold=2)
        expected_condition.add_subfulfillment(cc.Ed25519Fulfillment(public_key=user_vk))
        expected_condition.add_subfulfillment(cc.Ed25519Fulfillment(public_key=user2_vk))
        tx_expected_condition = {
            'details': expected_condition.to_dict(),
            'uri': expected_condition.condition.serialize_uri()
        }

        assert tx['transaction']['conditions'][0]['condition'] == tx_expected_condition

    def test_default_threshold_fulfillments_for_multiple_owners(self, b, user_sk, user_vk):
        user2_sk, user2_vk = crypto.generate_key_pair()

        # create transaction with multiple owners_after
        tx_create = b.create_transaction(b.me, [user_vk, user2_vk], None, 'CREATE')
        tx_create_signed = b.sign_transaction(tx_create, b.me_private)
        block = b.create_block([tx_create_signed])
        b.write_block(block, durability='hard')

        inputs = b.get_owned_ids(user_vk)

        # create a transaction with multiple current owners
        tx_transfer = b.create_transaction([user_vk, user2_vk], b.me, inputs, 'TRANSFER')
        tx_transfer_signed = b.sign_transaction(tx_transfer, [user_sk, user2_sk])

        # expected fulfillment
        expected_fulfillment = cc.Fulfillment.from_dict(
            tx_create['transaction']['conditions'][0]['condition']['details'])
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
                'details': first_tx_condition.to_dict(),
                'uri': first_tx_condition.condition.serialize_uri()
            },
            'cid': 0,
            'owners_after': None
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
        owned_count = len(b.get_owned_ids(user_vk))
        first_input_tx = b.get_owned_ids(user_vk).pop()

        hashlock_tx = b.create_transaction(user_vk, None, first_input_tx, 'TRANSFER')

        secret = b'much secret! wow!'
        first_tx_condition = cc.PreimageSha256Fulfillment(preimage=secret)

        hashlock_tx['transaction']['conditions'].append({
            'condition': {
                'details': first_tx_condition.to_dict(),
                'uri': first_tx_condition.condition.serialize_uri()
            },
            'cid': 0,
            'owners_after': None
        })
        # conditions have been updated, so hash needs updating
        hashlock_tx['id'] = util.get_hash_data(hashlock_tx)

        hashlock_tx_signed = b.sign_transaction(hashlock_tx, user_sk)

        assert b.validate_transaction(hashlock_tx_signed) == hashlock_tx_signed
        assert b.is_valid_transaction(hashlock_tx_signed) == hashlock_tx_signed
        assert len(b.get_owned_ids(user_vk)) == owned_count

        b.write_transaction(hashlock_tx_signed)

        # create and write block to bigchain
        block = b.create_block([hashlock_tx_signed])
        b.write_block(block, durability='hard')

        assert len(b.get_owned_ids(user_vk)) == owned_count - 1

    def test_create_and_fulfill_asset_with_hashlock_condition(self, b, user_vk):
        hashlock_tx = b.create_transaction(b.me, None, None, 'CREATE')

        secret = b'much secret! wow!'
        first_tx_condition = cc.PreimageSha256Fulfillment(preimage=secret)

        hashlock_tx['transaction']['conditions'].append({
            'condition': {
                'details': first_tx_condition.to_dict(),
                'uri': first_tx_condition.condition.serialize_uri()
            },
            'cid': 0,
            'owners_after': None
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
        hashlock_doublespend_tx = b.create_transaction(None, user2_vk, {'txid': hashlock_tx['id'], 'cid': 0},
                                                       'TRANSFER')

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
        owners_after = [user_vk, user2_vk, user3_vk, user4_vk, user5_vk]

        # create a transaction with multiple owners_after
        tx = b.create_transaction(b.me, owners_after, None, 'CREATE')
        condition = cc.Fulfillment.from_dict(tx['transaction']['conditions'][0]['condition']['details'])

        for owner_after in owners_after:
            subcondition = condition.get_subcondition_from_vk(owner_after)[0]
            assert subcondition.public_key.to_ascii().decode() == owner_after

    @pytest.mark.usefixtures('inputs')
    def test_transfer_asset_with_escrow_condition(self, b, user_vk, user_sk):
        first_input_tx = b.get_owned_ids(user_vk).pop()
        user2_sk, user2_vk = crypto.generate_key_pair()

        # ESCROW
        escrow_tx = b.create_transaction(user_vk, [user_vk, user2_vk], first_input_tx, 'TRANSFER')

        time_sleep = 3

        condition_escrow = cc.ThresholdSha256Fulfillment(threshold=1)
        fulfillment_timeout = cc.TimeoutFulfillment(expire_time=str(float(util.timestamp()) + time_sleep))
        fulfillment_timeout_inverted = cc.InvertedThresholdSha256Fulfillment(threshold=1)
        fulfillment_timeout_inverted.add_subfulfillment(fulfillment_timeout)  # invert the timeout condition
        condition_user = cc.Ed25519Fulfillment(public_key=user_vk)
        condition_user2 = cc.Ed25519Fulfillment(public_key=user2_vk)

        # execute branch
        fulfillment_and_execute = cc.ThresholdSha256Fulfillment(threshold=2)
        fulfillment_and_execute.add_subfulfillment(condition_user2)
        fulfillment_and_execute.add_subfulfillment(fulfillment_timeout)

        # do not fulfill abort branch
        fulfillment_and_abort = cc.ThresholdSha256Fulfillment(threshold=2)
        fulfillment_and_abort.add_subfulfillment(condition_user)
        fulfillment_and_abort.add_subfulfillment(fulfillment_timeout_inverted)

        condition_escrow.add_subfulfillment(fulfillment_and_execute)
        condition_escrow.add_subfulfillment(fulfillment_and_abort)

        # Update the condition in the newly created transaction
        escrow_tx['transaction']['conditions'][0]['condition'] = {
            'details': condition_escrow.to_dict(),
            'uri': condition_escrow.condition.serialize_uri()
        }

        # conditions have been updated, so hash needs updating
        escrow_tx['id'] = util.get_hash_data(escrow_tx)

        escrow_tx_signed = b.sign_transaction(escrow_tx, user_sk)

        assert b.validate_transaction(escrow_tx_signed) == escrow_tx_signed
        assert b.is_valid_transaction(escrow_tx_signed) == escrow_tx_signed

        b.write_transaction(escrow_tx_signed)

        # create and write block to bigchain
        block = b.create_block([escrow_tx_signed])
        b.write_block(block, durability='hard')

        # Retrieve the last transaction of thresholduser1_pub
        tx_retrieved_id = b.get_owned_ids(user2_vk).pop()

        # EXECUTE
        # Create a base template for output transaction
        escrow_tx_transfer = b.create_transaction([user_vk, user2_vk], user2_vk, tx_retrieved_id, 'TRANSFER')

        # Parse the threshold cryptocondition
        escrow_fulfillment = cc.Fulfillment.from_dict(
            escrow_tx['transaction']['conditions'][0]['condition']['details'])

        subfulfillment_user = escrow_fulfillment.get_subcondition_from_vk(user_vk)[0]
        subfulfillment_user2 = escrow_fulfillment.get_subcondition_from_vk(user2_vk)[0]

        # Get the fulfillment message to sign
        escrow_tx_fulfillment_message = util.get_fulfillment_message(escrow_tx_transfer,
                                                                     escrow_tx_transfer['transaction']['fulfillments'][0],
                                                                     serialized=True)
        escrow_fulfillment.subconditions = []
        # fulfill execute branch
        fulfillment_and_execute = cc.ThresholdSha256Fulfillment(threshold=2)
        subfulfillment_user2.sign(escrow_tx_fulfillment_message, crypto.SigningKey(user2_sk))
        fulfillment_and_execute.add_subfulfillment(subfulfillment_user2)
        fulfillment_and_execute.add_subfulfillment(fulfillment_timeout)
        escrow_fulfillment.add_subfulfillment(fulfillment_and_execute)

        # do not fulfill abort branch
        fulfillment_and_abort = cc.ThresholdSha256Fulfillment(threshold=2)
        fulfillment_and_abort.add_subfulfillment(subfulfillment_user)
        fulfillment_and_abort.add_subfulfillment(fulfillment_timeout_inverted)
        escrow_fulfillment.add_subcondition(fulfillment_and_abort.condition)

        escrow_tx_transfer['transaction']['fulfillments'][0]['fulfillment'] = escrow_fulfillment.serialize_uri()

        # in-time validation (execute)
        assert b.is_valid_transaction(escrow_tx_transfer) == escrow_tx_transfer
        assert b.validate_transaction(escrow_tx_transfer) == escrow_tx_transfer

        time.sleep(time_sleep + 1)

        assert b.is_valid_transaction(escrow_tx_transfer) is False
        with pytest.raises(exceptions.InvalidSignature):
            assert b.validate_transaction(escrow_tx_transfer) == escrow_tx_transfer

        # ABORT
        # Create a base template for output transaction
        escrow_tx_abort = b.create_transaction([user_vk, user2_vk], user_vk, tx_retrieved_id, 'TRANSFER')

        # Parse the threshold cryptocondition
        escrow_fulfillment = cc.Fulfillment.from_dict(
            escrow_tx['transaction']['conditions'][0]['condition']['details'])

        subfulfillment_user = escrow_fulfillment.get_subcondition_from_vk(user_vk)[0]
        subfulfillment_user2 = escrow_fulfillment.get_subcondition_from_vk(user2_vk)[0]

        # Get the fulfillment message to sign
        escrow_tx_fulfillment_message = util.get_fulfillment_message(escrow_tx_abort,
                                                                     escrow_tx_abort['transaction']['fulfillments'][0],
                                                                     serialized=True)
        escrow_fulfillment.subconditions = []
        # fulfill execute branch
        fulfillment_and_execute = cc.ThresholdSha256Fulfillment(threshold=2)
        fulfillment_and_execute.add_subfulfillment(subfulfillment_user2)
        fulfillment_and_execute.add_subfulfillment(fulfillment_timeout)
        escrow_fulfillment.add_subcondition(fulfillment_and_execute.condition)

        # do not fulfill abort branch
        fulfillment_and_abort = cc.ThresholdSha256Fulfillment(threshold=2)
        subfulfillment_user.sign(escrow_tx_fulfillment_message, crypto.SigningKey(user_sk))
        fulfillment_and_abort.add_subfulfillment(subfulfillment_user)
        fulfillment_and_abort.add_subfulfillment(fulfillment_timeout_inverted)
        escrow_fulfillment.add_subfulfillment(fulfillment_and_abort)

        escrow_tx_abort['transaction']['fulfillments'][0]['fulfillment'] = escrow_fulfillment.serialize_uri()

        # out-of-time validation (abort)
        assert b.validate_transaction(escrow_tx_abort) == escrow_tx_abort
        assert b.is_valid_transaction(escrow_tx_abort) == escrow_tx_abort

    @pytest.mark.usefixtures('inputs')
    def test_transfer_asset_with_escrow_condition_doublespend(self, b, user_vk, user_sk):
        first_input_tx = b.get_owned_ids(user_vk).pop()
        user2_sk, user2_vk = crypto.generate_key_pair()

        # ESCROW
        escrow_tx = b.create_transaction(user_vk, [user_vk, user2_vk], first_input_tx, 'TRANSFER')

        time_sleep = 3

        condition_escrow = cc.ThresholdSha256Fulfillment(threshold=1)
        fulfillment_timeout = cc.TimeoutFulfillment(expire_time=str(float(util.timestamp()) + time_sleep))
        fulfillment_timeout_inverted = cc.InvertedThresholdSha256Fulfillment(threshold=1)
        fulfillment_timeout_inverted.add_subfulfillment(fulfillment_timeout)  # invert the timeout condition
        condition_user = cc.Ed25519Fulfillment(public_key=user_vk)
        condition_user2 = cc.Ed25519Fulfillment(public_key=user2_vk)

        # execute branch
        fulfillment_and_execute = cc.ThresholdSha256Fulfillment(threshold=2)
        fulfillment_and_execute.add_subfulfillment(condition_user2)
        fulfillment_and_execute.add_subfulfillment(fulfillment_timeout)

        # do not fulfill abort branch
        fulfillment_and_abort = cc.ThresholdSha256Fulfillment(threshold=2)
        fulfillment_and_abort.add_subfulfillment(condition_user)
        fulfillment_and_abort.add_subfulfillment(fulfillment_timeout_inverted)

        condition_escrow.add_subfulfillment(fulfillment_and_execute)
        condition_escrow.add_subfulfillment(fulfillment_and_abort)

        # Update the condition in the newly created transaction
        escrow_tx['transaction']['conditions'][0]['condition'] = {
            'details': condition_escrow.to_dict(),
            'uri': condition_escrow.condition.serialize_uri()
        }

        # conditions have been updated, so hash needs updating
        escrow_tx['id'] = util.get_hash_data(escrow_tx)

        escrow_tx_signed = b.sign_transaction(escrow_tx, user_sk)

        assert b.validate_transaction(escrow_tx_signed) == escrow_tx_signed
        assert b.is_valid_transaction(escrow_tx_signed) == escrow_tx_signed

        b.write_transaction(escrow_tx_signed)

        # create and write block to bigchain
        block = b.create_block([escrow_tx_signed])
        b.write_block(block, durability='hard')

        # Retrieve the last transaction of thresholduser1_pub
        tx_retrieved_id = b.get_owned_ids(user2_vk).pop()

        # EXECUTE
        # Create a base template for output transaction
        escrow_tx_transfer = b.create_transaction([user_vk, user2_vk], user2_vk, tx_retrieved_id, 'TRANSFER')

        # Parse the threshold cryptocondition
        escrow_fulfillment = cc.Fulfillment.from_dict(
            escrow_tx['transaction']['conditions'][0]['condition']['details'])

        subfulfillment_user = escrow_fulfillment.get_subcondition_from_vk(user_vk)[0]
        subfulfillment_user2 = escrow_fulfillment.get_subcondition_from_vk(user2_vk)[0]

        # Get the fulfillment message to sign
        escrow_tx_fulfillment_message = util.get_fulfillment_message(escrow_tx_transfer,
                                                                     escrow_tx_transfer['transaction']['fulfillments'][0],
                                                                     serialized=True)
        escrow_fulfillment.subconditions = []
        # fulfill execute branch
        fulfillment_and_execute = cc.ThresholdSha256Fulfillment(threshold=2)
        subfulfillment_user2.sign(escrow_tx_fulfillment_message, crypto.SigningKey(user2_sk))
        fulfillment_and_execute.add_subfulfillment(subfulfillment_user2)
        fulfillment_and_execute.add_subfulfillment(fulfillment_timeout)
        escrow_fulfillment.add_subfulfillment(fulfillment_and_execute)

        # do not fulfill abort branch
        fulfillment_and_abort = cc.ThresholdSha256Fulfillment(threshold=2)
        fulfillment_and_abort.add_subfulfillment(subfulfillment_user)
        fulfillment_and_abort.add_subfulfillment(fulfillment_timeout_inverted)
        escrow_fulfillment.add_subcondition(fulfillment_and_abort.condition)

        escrow_tx_transfer['transaction']['fulfillments'][0]['fulfillment'] = escrow_fulfillment.serialize_uri()

        # in-time validation (execute)
        assert b.is_valid_transaction(escrow_tx_transfer) == escrow_tx_transfer
        assert b.validate_transaction(escrow_tx_transfer) == escrow_tx_transfer

        b.write_transaction(escrow_tx_transfer)

        # create and write block to bigchain
        block = b.create_block([escrow_tx_transfer])
        b.write_block(block, durability='hard')

        time.sleep(time_sleep + 1)

        assert b.is_valid_transaction(escrow_tx_transfer) is False
        with pytest.raises(exceptions.InvalidSignature):
            assert b.validate_transaction(escrow_tx_transfer) == escrow_tx_transfer

        # ABORT
        # Create a base template for output transaction
        escrow_tx_abort = b.create_transaction([user_vk, user2_vk], user_vk, tx_retrieved_id, 'TRANSFER')

        # Parse the threshold cryptocondition
        escrow_fulfillment = cc.Fulfillment.from_dict(
            escrow_tx['transaction']['conditions'][0]['condition']['details'])

        subfulfillment_user = escrow_fulfillment.get_subcondition_from_vk(user_vk)[0]
        subfulfillment_user2 = escrow_fulfillment.get_subcondition_from_vk(user2_vk)[0]

        # Get the fulfillment message to sign
        escrow_tx_fulfillment_message = util.get_fulfillment_message(escrow_tx_abort,
                                                                     escrow_tx_abort['transaction']['fulfillments'][0],
                                                                     serialized=True)
        escrow_fulfillment.subconditions = []
        # do not fulfill execute branch
        fulfillment_and_execute = cc.ThresholdSha256Fulfillment(threshold=2)
        fulfillment_and_execute.add_subfulfillment(subfulfillment_user2)
        fulfillment_and_execute.add_subfulfillment(fulfillment_timeout)
        escrow_fulfillment.add_subcondition(fulfillment_and_execute.condition)

        # fulfill abort branch
        fulfillment_and_abort = cc.ThresholdSha256Fulfillment(threshold=2)
        subfulfillment_user.sign(escrow_tx_fulfillment_message, crypto.SigningKey(user_sk))
        fulfillment_and_abort.add_subfulfillment(subfulfillment_user)
        fulfillment_and_abort.add_subfulfillment(fulfillment_timeout_inverted)
        escrow_fulfillment.add_subfulfillment(fulfillment_and_abort)

        escrow_tx_abort['transaction']['fulfillments'][0]['fulfillment'] = escrow_fulfillment.serialize_uri()

        # out-of-time validation (abort)
        with pytest.raises(exceptions.DoubleSpend):
            b.validate_transaction(escrow_tx_abort)
        assert b.is_valid_transaction(escrow_tx_abort) is False

