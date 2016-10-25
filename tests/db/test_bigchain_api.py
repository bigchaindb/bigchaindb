from time import sleep

import pytest


@pytest.mark.skipif(reason='Some tests throw a ResourceWarning that might result in some weird '
                           'exceptions while running the tests. The problem seems to *not* '
                           'interfere with the correctness of the tests. ')
def test_remove_unclosed_sockets():
    pass


# TODO: Get rid of this and move to conftest
def dummy_tx():
    import bigchaindb
    from bigchaindb.models import Transaction
    b = bigchaindb.Bigchain()
    tx = Transaction.create([b.me], [b.me])
    tx = tx.sign([b.me_private])
    return tx


# TODO: Get rid of this and move to conftest
def dummy_block():
    import bigchaindb
    b = bigchaindb.Bigchain()
    block = b.create_block([dummy_tx()])
    return block


class TestBigchainApi(object):
    def test_get_last_voted_block_cyclic_blockchain(self, b, monkeypatch):
        from bigchaindb.common.crypto import SigningKey
        from bigchaindb.common.exceptions import CyclicBlockchainError
        from bigchaindb.common.util import serialize
        from bigchaindb.models import Transaction

        b.create_genesis_block()

        tx = Transaction.create([b.me], [b.me])
        tx = tx.sign([b.me_private])
        monkeypatch.setattr('time.time', lambda: 1)
        block1 = b.create_block([tx])
        b.write_block(block1, durability='hard')

        # Manipulate vote to create a cyclic Blockchain
        vote = b.vote(block1.id, b.get_last_voted_block().id, True)
        vote['vote']['previous_block'] = block1.id
        vote_data = serialize(vote['vote'])
        vote['signature'] = SigningKey(b.me_private).sign(vote_data.encode())
        b.write_vote(vote)

        with pytest.raises(CyclicBlockchainError):
            b.get_last_voted_block()

    def test_try_voting_while_constructing_cyclic_blockchain(self, b,
                                                             monkeypatch):
        from bigchaindb.common.exceptions import CyclicBlockchainError
        from bigchaindb.models import Transaction

        b.create_genesis_block()

        tx = Transaction.create([b.me], [b.me])
        tx = tx.sign([b.me_private])
        block1 = b.create_block([tx])

        # We can simply submit twice the same block id and check if `Bigchain`
        # throws
        with pytest.raises(CyclicBlockchainError):
            b.vote(block1.id, block1.id, True)

    def test_has_previous_vote_when_already_voted(self, b, monkeypatch):
        from bigchaindb.models import Transaction

        b.create_genesis_block()

        tx = Transaction.create([b.me], [b.me])
        tx = tx.sign([b.me_private])

        monkeypatch.setattr('time.time', lambda: 1)
        block = b.create_block([tx])
        b.write_block(block, durability='hard')

        assert b.has_previous_vote(block.id, block.voters) is False

        vote = b.vote(block.id, b.get_last_voted_block().id, True)
        b.write_vote(vote)

        assert b.has_previous_vote(block.id, block.voters) is True


    def test_get_transactions_for_metadata_mismatch(self, b):
        matches = b.get_tx_by_metadata_id('missing')
        assert not matches

    def test_get_spent_with_double_spend(self, b, monkeypatch):
        from bigchaindb.common.exceptions import DoubleSpend
        from bigchaindb.models import Transaction

        b.create_genesis_block()

        tx = Transaction.create([b.me], [b.me])
        tx = tx.sign([b.me_private])

        monkeypatch.setattr('time.time', lambda: 1)
        block1 = b.create_block([tx])
        b.write_block(block1, durability='hard')

        monkeypatch.setattr('time.time', lambda: 2)
        transfer_tx = Transaction.transfer(tx.to_inputs(), [b.me], tx.asset)
        transfer_tx = transfer_tx.sign([b.me_private])
        block2 = b.create_block([transfer_tx])
        b.write_block(block2, durability='hard')

        monkeypatch.setattr('time.time', lambda: 3)
        transfer_tx2 = Transaction.transfer(tx.to_inputs(), [b.me], tx.asset)
        transfer_tx2 = transfer_tx2.sign([b.me_private])
        block3 = b.create_block([transfer_tx2])
        b.write_block(block3, durability='hard')

        # Vote both block2 and block3 valid to provoke a double spend
        vote = b.vote(block2.id, b.get_last_voted_block().id, True)
        b.write_vote(vote)
        vote = b.vote(block3.id, b.get_last_voted_block().id, True)
        b.write_vote(vote)

        with pytest.raises(DoubleSpend):
            b.get_spent(tx.id, 0)

    def test_get_block_status_for_tx_with_double_spend(self, b, monkeypatch):
        from bigchaindb.common.exceptions import DoubleSpend
        from bigchaindb.models import Transaction

        b.create_genesis_block()

        tx = Transaction.create([b.me], [b.me])
        tx = tx.sign([b.me_private])

        monkeypatch.setattr('time.time', lambda: 1)
        block1 = b.create_block([tx])
        b.write_block(block1, durability='hard')

        monkeypatch.setattr('time.time', lambda: 2)
        block2 = b.create_block([tx])
        b.write_block(block2, durability='hard')

        # Vote both blocks valid (creating a double spend)
        vote = b.vote(block1.id, b.get_last_voted_block().id, True)
        b.write_vote(vote)
        vote = b.vote(block2.id, b.get_last_voted_block().id, True)
        b.write_vote(vote)

        with pytest.raises(DoubleSpend):
            b.get_blocks_status_containing_tx(tx.id)

    def test_get_transaction_in_invalid_and_valid_block(self, monkeypatch, b):
        from bigchaindb.models import Transaction

        b.create_genesis_block()

        monkeypatch.setattr('time.time', lambda: 1)
        tx1 = Transaction.create([b.me], [b.me])
        tx1 = tx1.sign([b.me_private])
        block1 = b.create_block([tx1])
        b.write_block(block1, durability='hard')

        monkeypatch.setattr('time.time', lambda: 2)
        tx2 = Transaction.create([b.me], [b.me])
        tx2 = tx2.sign([b.me_private])
        block2 = b.create_block([tx2])
        b.write_block(block2, durability='hard')

        # vote the first block invalid
        vote = b.vote(block1.id, b.get_last_voted_block().id, False)
        b.write_vote(vote)

        # vote the second block valid
        vote = b.vote(block2.id, b.get_last_voted_block().id, True)
        b.write_vote(vote)

        assert b.get_transaction(tx1.id) is None
        assert b.get_transaction(tx2.id) == tx2

    def test_get_transactions_for_metadata(self, b, user_vk):
        from bigchaindb.models import Transaction

        metadata = {'msg': 'Hello BigchainDB!'}
        tx = Transaction.create([b.me], [user_vk], metadata=metadata)

        block = b.create_block([tx])
        b.write_block(block, durability='hard')

        matches = b.get_tx_by_payload_uuid(tx.metadata.data_id)
        assert len(matches) == 1
        assert matches[0].id == tx.id

    def test_get_transactions_for_metadata(self, b, user_vk):
        matches = b.get_tx_by_metadata_id('missing')
        assert not matches

    @pytest.mark.usefixtures('inputs')
    def test_write_transaction(self, b, user_vk, user_sk):
        from bigchaindb.models import Transaction

        input_tx = b.get_owned_ids(user_vk).pop()
        input_tx = b.get_transaction(input_tx.txid)
        inputs = input_tx.to_inputs()
        tx = Transaction.transfer(inputs, [user_vk], input_tx.asset)
        tx = tx.sign([user_sk])
        response = b.write_transaction(tx)

        assert response['skipped'] == 0
        assert response['deleted'] == 0
        assert response['unchanged'] == 0
        assert response['errors'] == 0
        assert response['replaced'] == 0
        assert response['inserted'] == 1

    @pytest.mark.usefixtures('inputs')
    def test_read_transaction(self, b, user_vk, user_sk):
        from bigchaindb.models import Transaction

        input_tx = b.get_owned_ids(user_vk).pop()
        input_tx = b.get_transaction(input_tx.txid)
        inputs = input_tx.to_inputs()
        tx = Transaction.transfer(inputs, [user_vk], input_tx.asset)
        tx = tx.sign([user_sk])
        b.write_transaction(tx)

        # create block and write it to the bighcain before retrieving the transaction
        block = b.create_block([tx])
        b.write_block(block, durability='hard')

        response, status = b.get_transaction(tx.id, include_status=True)
        # add validity information, which will be returned
        assert tx.to_dict() == response.to_dict()
        assert status == b.TX_UNDECIDED

    @pytest.mark.usefixtures('inputs')
    def test_read_transaction_invalid_block(self, b, user_vk, user_sk):
        from bigchaindb.models import Transaction

        input_tx = b.get_owned_ids(user_vk).pop()
        input_tx = b.get_transaction(input_tx.txid)
        inputs = input_tx.to_inputs()
        tx = Transaction.transfer(inputs, [user_vk], input_tx.asset)
        tx = tx.sign([user_sk])
        b.write_transaction(tx)

        # create block
        block = b.create_block([tx])
        b.write_block(block, durability='hard')

        # vote the block invalid
        vote = b.vote(block.id, b.get_last_voted_block().id, False)
        b.write_vote(vote)
        response = b.get_transaction(tx.id)

        # should be None, because invalid blocks are ignored
        assert response is None

    @pytest.mark.usefixtures('inputs')
    def test_genesis_block(self, b):
        import rethinkdb as r
        from bigchaindb.util import is_genesis_block
        from bigchaindb.db.utils import get_conn

        response = list(r.table('bigchain')
                        .filter(is_genesis_block)
                        .run(get_conn()))

        assert len(response) == 1
        block = response[0]
        assert len(block['block']['transactions']) == 1
        assert block['block']['transactions'][0]['transaction']['operation'] == 'GENESIS'
        assert block['block']['transactions'][0]['transaction']['fulfillments'][0]['input'] is None

    def test_create_genesis_block_fails_if_table_not_empty(self, b):
        import rethinkdb as r
        from bigchaindb.common.exceptions import GenesisBlockAlreadyExistsError
        from bigchaindb.util import is_genesis_block
        from bigchaindb.db.utils import get_conn

        b.create_genesis_block()

        with pytest.raises(GenesisBlockAlreadyExistsError):
            b.create_genesis_block()

        genesis_blocks = list(r.table('bigchain')
                              .filter(is_genesis_block)
                              .run(get_conn()))

        assert len(genesis_blocks) == 1

    @pytest.mark.skipif(reason='This test may not make sense after changing the chainification mode')
    def test_get_last_block(self, b):
        import rethinkdb as r
        from bigchaindb.db.utils import get_conn

        # get the number of blocks
        num_blocks = r.table('bigchain').count().run(get_conn())

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

    def test_create_empty_block(self, b):
        from bigchaindb.common.exceptions import OperationError

        with pytest.raises(OperationError) as excinfo:
            b.create_block([])

        assert excinfo.value.args[0] == 'Empty block creation is not allowed'

    def test_get_last_voted_block_returns_genesis_if_no_votes_has_been_casted(self, b):
        import rethinkdb as r
        from bigchaindb import util
        from bigchaindb.models import Block
        from bigchaindb.db.utils import get_conn

        b.create_genesis_block()
        genesis = list(r.table('bigchain')
                       .filter(util.is_genesis_block)
                       .run(get_conn()))[0]
        genesis = Block.from_dict(genesis)
        gb = b.get_last_voted_block()
        assert gb == genesis
        assert b.validate_block(gb) == gb

    def test_get_last_voted_block_returns_the_correct_block_same_timestamp(self, b, monkeypatch):
        genesis = b.create_genesis_block()

        assert b.get_last_voted_block() == genesis

        monkeypatch.setattr('time.time', lambda: 1)
        block_1 = dummy_block()
        monkeypatch.setattr('time.time', lambda: 2)
        block_2 = dummy_block()
        monkeypatch.setattr('time.time', lambda: 3)
        block_3 = dummy_block()

        b.write_block(block_1, durability='hard')
        b.write_block(block_2, durability='hard')
        b.write_block(block_3, durability='hard')

        # make sure all the votes are written with the same timestamps
        monkeypatch.setattr('time.time', lambda: 4)
        b.write_vote(b.vote(block_1.id, b.get_last_voted_block().id, True))
        assert b.get_last_voted_block().id == block_1.id

        b.write_vote(b.vote(block_2.id, b.get_last_voted_block().id, True))
        assert b.get_last_voted_block().id == block_2.id

        b.write_vote(b.vote(block_3.id, b.get_last_voted_block().id, True))
        assert b.get_last_voted_block().id == block_3.id

    def test_get_last_voted_block_returns_the_correct_block_different_timestamps(self, b, monkeypatch):
        genesis = b.create_genesis_block()

        assert b.get_last_voted_block() == genesis

        monkeypatch.setattr('time.time', lambda: 1)
        block_1 = dummy_block()
        monkeypatch.setattr('time.time', lambda: 2)
        block_2 = dummy_block()
        monkeypatch.setattr('time.time', lambda: 3)
        block_3 = dummy_block()

        b.write_block(block_1, durability='hard')
        b.write_block(block_2, durability='hard')
        b.write_block(block_3, durability='hard')

        # make sure all the votes are written with different timestamps
        monkeypatch.setattr('time.time', lambda: 4)
        b.write_vote(b.vote(block_1.id, b.get_last_voted_block().id, True))
        assert b.get_last_voted_block().id == block_1.id

        monkeypatch.setattr('time.time', lambda: 5)
        b.write_vote(b.vote(block_2.id, b.get_last_voted_block().id, True))
        assert b.get_last_voted_block().id == block_2.id

        monkeypatch.setattr('time.time', lambda: 6)
        b.write_vote(b.vote(block_3.id, b.get_last_voted_block().id, True))
        assert b.get_last_voted_block().id == block_3.id

    def test_no_vote_written_if_block_already_has_vote(self, b):
        import rethinkdb as r
        from bigchaindb.models import Block
        from bigchaindb.db.utils import get_conn

        genesis = b.create_genesis_block()
        block_1 = dummy_block()
        b.write_block(block_1, durability='hard')

        b.write_vote(b.vote(block_1.id, genesis.id, True))
        retrieved_block_1 = r.table('bigchain').get(block_1.id).run(get_conn())
        retrieved_block_1 = Block.from_dict(retrieved_block_1)

        # try to vote again on the retrieved block, should do nothing
        b.write_vote(b.vote(retrieved_block_1.id, genesis.id, True))
        retrieved_block_2 = r.table('bigchain').get(block_1.id).run(get_conn())
        retrieved_block_2 = Block.from_dict(retrieved_block_2)

        assert retrieved_block_1 == retrieved_block_2

    def test_more_votes_than_voters(self, b):
        import rethinkdb as r
        from bigchaindb.common.exceptions import MultipleVotesError
        from bigchaindb.db.utils import get_conn

        b.create_genesis_block()
        block_1 = dummy_block()
        b.write_block(block_1, durability='hard')
        # insert duplicate votes
        vote_1 = b.vote(block_1.id, b.get_last_voted_block().id, True)
        vote_2 = b.vote(block_1.id, b.get_last_voted_block().id, True)
        vote_2['node_pubkey'] = 'aaaaaaa'
        r.table('votes').insert(vote_1).run(get_conn())
        r.table('votes').insert(vote_2).run(get_conn())

        with pytest.raises(MultipleVotesError) as excinfo:
            b.block_election_status(block_1.id, block_1.voters)
        assert excinfo.value.args[0] == 'Block {block_id} has {n_votes} votes cast, but only {n_voters} voters'\
            .format(block_id=block_1.id, n_votes=str(2), n_voters=str(1))

    def test_multiple_votes_single_node(self, b):
        import rethinkdb as r
        from bigchaindb.common.exceptions import MultipleVotesError
        from bigchaindb.db.utils import get_conn

        genesis = b.create_genesis_block()
        block_1 = dummy_block()
        b.write_block(block_1, durability='hard')
        # insert duplicate votes
        for i in range(2):
            r.table('votes').insert(b.vote(block_1.id, genesis.id, True)).run(get_conn())

        with pytest.raises(MultipleVotesError) as excinfo:
            b.block_election_status(block_1.id, block_1.voters)
        assert excinfo.value.args[0] == 'Block {block_id} has multiple votes ({n_votes}) from voting node {node_id}'\
            .format(block_id=block_1.id, n_votes=str(2), node_id=b.me)

        with pytest.raises(MultipleVotesError) as excinfo:
            b.has_previous_vote(block_1.id, block_1.voters)
        assert excinfo.value.args[0] == 'Block {block_id} has {n_votes} votes from public key {me}'\
            .format(block_id=block_1.id, n_votes=str(2), me=b.me)

    def test_improper_vote_error(selfs, b):
        import rethinkdb as r
        from bigchaindb.common.exceptions import ImproperVoteError
        from bigchaindb.db.utils import get_conn

        b.create_genesis_block()
        block_1 = dummy_block()
        b.write_block(block_1, durability='hard')
        vote_1 = b.vote(block_1.id, b.get_last_voted_block().id, True)
        # mangle the signature
        vote_1['signature'] = 'a' * 87
        r.table('votes').insert(vote_1).run(get_conn())
        with pytest.raises(ImproperVoteError) as excinfo:
            b.has_previous_vote(block_1.id, block_1.id)
        assert excinfo.value.args[0] == 'Block {block_id} already has an incorrectly signed ' \
                                        'vote from public key {me}'.format(block_id=block_1.id, me=b.me)

    @pytest.mark.usefixtures('inputs')
    def test_assign_transaction_one_node(self, b, user_vk, user_sk):
        import rethinkdb as r
        from bigchaindb.models import Transaction
        from bigchaindb.db.utils import get_conn

        input_tx = b.get_owned_ids(user_vk).pop()
        input_tx = b.get_transaction(input_tx.txid)
        inputs = input_tx.to_inputs()
        tx = Transaction.transfer(inputs, [user_vk], input_tx.asset)
        tx = tx.sign([user_sk])
        b.write_transaction(tx)

        # retrieve the transaction
        response = r.table('backlog').get(tx.id).run(get_conn())

        # check if the assignee is the current node
        assert response['assignee'] == b.me

    @pytest.mark.usefixtures('inputs')
    def test_assign_transaction_multiple_nodes(self, b, user_vk, user_sk):
        import rethinkdb as r
        from bigchaindb.common.crypto import generate_key_pair
        from bigchaindb.models import Transaction
        from bigchaindb.db.utils import get_conn

        # create 5 federation nodes
        for _ in range(5):
            b.nodes_except_me.append(generate_key_pair()[1])

        # test assignee for several transactions
        for _ in range(20):
            input_tx = b.get_owned_ids(user_vk).pop()
            input_tx = b.get_transaction(input_tx.txid)
            inputs = input_tx.to_inputs()
            tx = Transaction.transfer(inputs, [user_vk], input_tx.asset)
            tx = tx.sign([user_sk])
            b.write_transaction(tx)

            # retrieve the transaction
            response = r.table('backlog').get(tx.id).run(get_conn())

            # check if the assignee is one of the _other_ federation nodes
            assert response['assignee'] in b.nodes_except_me


    @pytest.mark.usefixtures('inputs')
    def test_non_create_input_not_found(self, b, user_vk):
        from cryptoconditions import Ed25519Fulfillment
        from bigchaindb.common.exceptions import TransactionDoesNotExist
        from bigchaindb.common.transaction import (Fulfillment, Asset,
                                                   TransactionLink)
        from bigchaindb.models import Transaction
        from bigchaindb import Bigchain

        # Create a fulfillment for a non existing transaction
        fulfillment = Fulfillment(Ed25519Fulfillment(public_key=user_vk),
                                  [user_vk],
                                  TransactionLink('somethingsomething', 0))
        tx = Transaction.transfer([fulfillment], [user_vk], Asset())

        with pytest.raises(TransactionDoesNotExist) as excinfo:
            tx.validate(Bigchain())


class TestTransactionValidation(object):
    def test_create_operation_with_inputs(self, b, user_vk, create_tx):
        from bigchaindb.common.transaction import TransactionLink

        # Manipulate fulfillment so that it has a `tx_input` defined even
        # though it shouldn't have one
        create_tx.fulfillments[0].tx_input = TransactionLink('abc', 0)
        with pytest.raises(ValueError) as excinfo:
            b.validate_transaction(create_tx)
        assert excinfo.value.args[0] == 'A CREATE operation has no inputs'

    def test_transfer_operation_no_inputs(self, b, user_vk,
                                          signed_transfer_tx):
        signed_transfer_tx.fulfillments[0].tx_input = None
        with pytest.raises(ValueError) as excinfo:
            b.validate_transaction(signed_transfer_tx)

        assert excinfo.value.args[0] == 'Only `CREATE` transactions can have null inputs'

    def test_non_create_input_not_found(self, b, user_vk, signed_transfer_tx):
        from bigchaindb.common.exceptions import TransactionDoesNotExist
        from bigchaindb.common.transaction import TransactionLink

        signed_transfer_tx.fulfillments[0].tx_input = TransactionLink('c', 0)
        with pytest.raises(TransactionDoesNotExist):
            b.validate_transaction(signed_transfer_tx)

    @pytest.mark.usefixtures('inputs')
    def test_non_create_valid_input_wrong_owner(self, b, user_vk):
        from bigchaindb.common.crypto import generate_key_pair
        from bigchaindb.common.exceptions import InvalidSignature
        from bigchaindb.models import Transaction

        input_tx = b.get_owned_ids(user_vk).pop()
        input_transaction = b.get_transaction(input_tx.txid)
        sk, vk = generate_key_pair()
        tx = Transaction.create([vk], [user_vk])
        tx.operation = 'TRANSFER'
        tx.asset = input_transaction.asset
        tx.fulfillments[0].tx_input = input_tx

        with pytest.raises(InvalidSignature):
            b.validate_transaction(tx)

    @pytest.mark.usefixtures('inputs')
    def test_non_create_double_spend(self, b, signed_create_tx,
                                     signed_transfer_tx):
        from bigchaindb.common.exceptions import DoubleSpend

        block1 = b.create_block([signed_create_tx])
        b.write_block(block1)

        # vote block valid
        vote = b.vote(block1.id, b.get_last_voted_block().id, True)
        b.write_vote(vote)

        b.write_transaction(signed_transfer_tx)
        block = b.create_block([signed_transfer_tx])
        b.write_block(block, durability='hard')

        # vote block valid
        vote = b.vote(block.id, b.get_last_voted_block().id, True)
        b.write_vote(vote)

        sleep(1)

        signed_transfer_tx.timestamp = 123
        # FIXME: https://github.com/bigchaindb/bigchaindb/issues/592
        with pytest.raises(DoubleSpend):
            b.validate_transaction(signed_transfer_tx)

    @pytest.mark.usefixtures('inputs')
    def test_valid_non_create_transaction_after_block_creation(self, b,
                                                               user_vk,
                                                               user_sk):
        from bigchaindb.models import Transaction

        input_tx = b.get_owned_ids(user_vk).pop()
        input_tx = b.get_transaction(input_tx.txid)
        inputs = input_tx.to_inputs()
        transfer_tx = Transaction.transfer(inputs, [user_vk], input_tx.asset)
        transfer_tx = transfer_tx.sign([user_sk])

        assert transfer_tx == b.validate_transaction(transfer_tx)

        # create block
        block = b.create_block([transfer_tx])
        assert b.validate_block(block) == block
        b.write_block(block, durability='hard')

        # check that the transaction is still valid after being written to the
        # bigchain
        assert transfer_tx == b.validate_transaction(transfer_tx)

    @pytest.mark.usefixtures('inputs')
    def test_fulfillment_not_in_valid_block(self, b, user_vk, user_sk):
        from bigchaindb.models import Transaction
        from bigchaindb.common.exceptions import FulfillmentNotInValidBlock

        input_tx = b.get_owned_ids(user_vk).pop()
        input_tx = b.get_transaction(input_tx.txid)
        inputs = input_tx.to_inputs()

        # create a transaction that's valid but not in a voted valid block
        transfer_tx = Transaction.transfer(inputs, [user_vk], input_tx.asset)
        transfer_tx = transfer_tx.sign([user_sk])

        assert transfer_tx == b.validate_transaction(transfer_tx)

        # create block
        block = b.create_block([transfer_tx])
        b.write_block(block, durability='hard')

        # create transaction with the undecided input
        tx_invalid = Transaction.transfer(transfer_tx.to_inputs(), [user_vk],
                                         transfer_tx.asset)
        tx_invalid = tx_invalid.sign([user_sk])

        with pytest.raises(FulfillmentNotInValidBlock):
            b.validate_transaction(tx_invalid)


class TestBlockValidation(object):
    @pytest.mark.skipif(reason='Separated tx validation from block creation.')
    @pytest.mark.usefixtures('inputs')
    def test_invalid_transactions_in_block(self, b, user_vk):
        from bigchaindb.common import crypto
        from bigchaindb.common.exceptions import TransactionOwnerError
        from bigchaindb.common.util import gen_timestamp

        from bigchaindb import util

        # invalid transaction
        valid_input = b.get_owned_ids(user_vk).pop()
        tx_invalid = b.create_transaction('a', 'b', valid_input, 'c')

        block = b.create_block([tx_invalid])

        # create a block with invalid transactions
        block = {
            'timestamp': gen_timestamp(),
            'transactions': [tx_invalid],
            'node_pubkey': b.me,
            'voters': b.nodes_except_me
        }

        # NOTE: This is not the correct function anymore, but this test is
        #       skipped
        block_data = util.serialize_block(block)
        block_hash = crypto.hash_data(block_data)
        block_signature = crypto.SigningKey(b.me_private).sign(block_data)

        block = {
            'id': block_hash,
            'block': block,
            'signature': block_signature,
            'votes': []
        }

        with pytest.raises(TransactionOwnerError) as excinfo:
            # TODO: Adjust this to the new Block model (test is currently
            #       skipped.
            b.validate_block(block)

        assert excinfo.value.args[0] == 'owner_before `a` does not own the input `{}`'.format(valid_input)

    def test_invalid_signature(self, b):
        from bigchaindb.common.exceptions import InvalidSignature
        from bigchaindb.common import crypto

        # create a valid block
        block = dummy_block()

        # replace the block signature with an invalid one
        block.signature = crypto.SigningKey(b.me_private).sign(b'wrongdata')

        # check that validate_block raises an InvalidSignature exception
        with pytest.raises(InvalidSignature):
            b.validate_block(block)

    def test_invalid_node_pubkey(self, b):
        from bigchaindb.common.exceptions import OperationError
        from bigchaindb.common import crypto

        # blocks can only be created by a federation node
        # create a valid block
        block = dummy_block()

        # create some temp keys
        tmp_sk, tmp_vk = crypto.generate_key_pair()

        # change the block node_pubkey
        block.node_pubkey = tmp_vk

        # just to make sure lets re-hash the block and create a valid signature
        # from a non federation node
        block = block.sign(tmp_sk)

        # check that validate_block raises an OperationError
        with pytest.raises(OperationError):
            b.validate_block(block)


class TestMultipleInputs(object):
    def test_transfer_single_owner_single_input(self, b, inputs, user_vk,
                                                user_sk):
        from bigchaindb.common import crypto
        from bigchaindb.models import Transaction
        user2_sk, user2_vk = crypto.generate_key_pair()

        tx_link = b.get_owned_ids(user_vk).pop()
        input_tx = b.get_transaction(tx_link.txid)
        inputs = input_tx.to_inputs()
        tx = Transaction.transfer(inputs, [user2_vk], input_tx.asset)
        tx = tx.sign([user_sk])

        # validate transaction
        assert b.is_valid_transaction(tx) == tx
        assert len(tx.fulfillments) == 1
        assert len(tx.conditions) == 1

    @pytest.mark.skipif(reason=('Multiple inputs are only allowed for the '
                                'same asset. Remove this after implementing ',
                                'multiple assets'))
    @pytest.mark.usefixtures('inputs')
    def test_transfer_single_owners_multiple_inputs(self, b, user_sk, user_vk):
        from bigchaindb.common import crypto
        from bigchaindb.models import Transaction

        user2_sk, user2_vk = crypto.generate_key_pair()

        # get inputs
        owned_inputs = b.get_owned_ids(user_vk)
        input_txs = [b.get_transaction(tx_link.txid) for tx_link
                     in owned_inputs]
        inputs = sum([input_tx.to_inputs() for input_tx in input_txs], [])
        tx = Transaction.transfer(inputs, len(inputs) * [[user_vk]])
        tx = tx.sign([user_sk])
        assert b.validate_transaction(tx) == tx
        assert len(tx.fulfillments) == len(inputs)
        assert len(tx.conditions) == len(inputs)

    @pytest.mark.skipif(reason=('Multiple inputs are only allowed for the '
                                'same asset. Remove this after implementing ',
                                'multiple assets'))
    @pytest.mark.usefixtures('inputs')
    def test_transfer_single_owners_single_input_from_multiple_outputs(self, b,
                                                                       user_sk,
                                                                       user_vk):
        from bigchaindb.common import crypto
        from bigchaindb.models import Transaction

        user2_sk, user2_vk = crypto.generate_key_pair()

        # get inputs
        owned_inputs = b.get_owned_ids(user_vk)
        input_txs = [b.get_transaction(tx_link.txid) for tx_link
                     in owned_inputs]
        inputs = sum([input_tx.to_inputs() for input_tx in input_txs], [])
        tx = Transaction.transfer(inputs, len(inputs) * [[user2_vk]])
        tx = tx.sign([user_sk])

        # create block with the transaction
        block = b.create_block([tx])
        b.write_block(block, durability='hard')

        # vote block valid
        vote = b.vote(block.id, b.get_last_voted_block().id, True)
        b.write_vote(vote)

        # get inputs from user2
        owned_inputs = b.get_owned_ids(user2_vk)
        assert len(owned_inputs) == len(inputs)

        # create a transaction with a single input from a multiple output transaction
        tx_link = owned_inputs.pop()
        inputs = b.get_transaction(tx_link.txid).to_inputs([0])
        tx = Transaction.transfer(inputs, [user_vk])
        tx = tx.sign([user2_sk])

        assert b.is_valid_transaction(tx) == tx
        assert len(tx.fulfillments) == 1
        assert len(tx.conditions) == 1

    def test_single_owner_before_multiple_owners_after_single_input(self, b,
                                                                    user_sk,
                                                                    user_vk,
                                                                    inputs):
        from bigchaindb.common import crypto
        from bigchaindb.models import Transaction

        user2_sk, user2_vk = crypto.generate_key_pair()
        user3_sk, user3_vk = crypto.generate_key_pair()

        owned_inputs = b.get_owned_ids(user_vk)
        tx_link = owned_inputs.pop()
        input_tx = b.get_transaction(tx_link.txid)
        tx = Transaction.transfer(input_tx.to_inputs(), [[user2_vk, user3_vk]], input_tx.asset)
        tx = tx.sign([user_sk])

        assert b.is_valid_transaction(tx) == tx
        assert len(tx.fulfillments) == 1
        assert len(tx.conditions) == 1

    @pytest.mark.skipif(reason=('Multiple inputs are only allowed for the '
                                'same asset. Remove this after implementing ',
                                'multiple assets'))
    @pytest.mark.usefixtures('inputs')
    def test_single_owner_before_multiple_owners_after_multiple_inputs(self, b,
                                                                       user_sk,
                                                                       user_vk):
        from bigchaindb.common import crypto
        from bigchaindb.models import Transaction

        user2_sk, user2_vk = crypto.generate_key_pair()
        user3_sk, user3_vk = crypto.generate_key_pair()

        owned_inputs = b.get_owned_ids(user_vk)
        input_txs = [b.get_transaction(tx_link.txid) for tx_link
                     in owned_inputs]
        inputs = sum([input_tx.to_inputs() for input_tx in input_txs], [])

        tx = Transaction.transfer(inputs, len(inputs) * [[user2_vk, user3_vk]])
        tx = tx.sign([user_sk])

        # create block with the transaction
        block = b.create_block([tx])
        b.write_block(block, durability='hard')

        # vote block valid
        vote = b.vote(block.id, b.get_last_voted_block().id, True)
        b.write_vote(vote)

        # validate transaction
        assert b.is_valid_transaction(tx) == tx
        assert len(tx.fulfillments) == len(inputs)
        assert len(tx.conditions) == len(inputs)

    @pytest.mark.usefixtures('inputs')
    def test_multiple_owners_before_single_owner_after_single_input(self, b,
                                                                    user_sk,
                                                                    user_vk):
        from bigchaindb.common import crypto
        from bigchaindb.models import Transaction

        user2_sk, user2_vk = crypto.generate_key_pair()
        user3_sk, user3_vk = crypto.generate_key_pair()

        tx = Transaction.create([b.me], [user_vk, user2_vk])
        tx = tx.sign([b.me_private])
        block = b.create_block([tx])
        b.write_block(block, durability='hard')

        # vote block valid
        vote = b.vote(block.id, b.get_last_voted_block().id, True)
        b.write_vote(vote)

        owned_input = b.get_owned_ids(user_vk).pop()
        input_tx = b.get_transaction(owned_input.txid)
        inputs = input_tx.to_inputs()

        transfer_tx = Transaction.transfer(inputs, [user3_vk], input_tx.asset)
        transfer_tx = transfer_tx.sign([user_sk, user2_sk])

        # validate transaction
        assert b.is_valid_transaction(transfer_tx) == transfer_tx
        assert len(transfer_tx.fulfillments) == 1
        assert len(transfer_tx.conditions) == 1

    @pytest.mark.skipif(reason=('Multiple inputs are only allowed for the '
                                'same asset. Remove this after implementing ',
                                'multiple assets'))
    @pytest.mark.usefixtures('inputs_shared')
    def test_multiple_owners_before_single_owner_after_multiple_inputs(self, b,
                                          user_sk, user_vk, user2_vk, user2_sk):
        from bigchaindb.common import crypto
        from bigchaindb.models import Transaction

        # create a new users
        user3_sk, user3_vk = crypto.generate_key_pair()

        tx_links = b.get_owned_ids(user_vk)
        inputs = sum([b.get_transaction(tx_link.txid).to_inputs() for tx_link
                      in tx_links], [])

        tx = Transaction.transfer(inputs, len(inputs) * [[user3_vk]])
        tx = tx.sign([user_sk, user2_sk])

        assert b.is_valid_transaction(tx) == tx
        assert len(tx.fulfillments) == len(inputs)
        assert len(tx.conditions) == len(inputs)

    @pytest.mark.usefixtures('inputs')
    def test_multiple_owners_before_multiple_owners_after_single_input(self, b,
                                                                       user_sk,
                                                                       user_vk):
        from bigchaindb.common import crypto
        from bigchaindb.models import Transaction

        user2_sk, user2_vk = crypto.generate_key_pair()
        user3_sk, user3_vk = crypto.generate_key_pair()
        user4_sk, user4_vk = crypto.generate_key_pair()

        tx = Transaction.create([b.me], [user_vk, user2_vk])
        tx = tx.sign([b.me_private])
        block = b.create_block([tx])
        b.write_block(block, durability='hard')

        # vote block valid
        vote = b.vote(block.id, b.get_last_voted_block().id, True)
        b.write_vote(vote)

        # get input
        tx_link = b.get_owned_ids(user_vk).pop()
        tx_input = b.get_transaction(tx_link.txid)

        tx = Transaction.transfer(tx_input.to_inputs(), [[user3_vk, user4_vk]], tx_input.asset)
        tx = tx.sign([user_sk, user2_sk])

        assert b.is_valid_transaction(tx) == tx
        assert len(tx.fulfillments) == 1
        assert len(tx.conditions) == 1

    @pytest.mark.skipif(reason=('Multiple inputs are only allowed for the '
                                'same asset. Remove this after implementing ',
                                'multiple assets'))
    @pytest.mark.usefixtures('inputs_shared')
    def test_multiple_owners_before_multiple_owners_after_multiple_inputs(self, b,
                                                                user_sk, user_vk,
                                                                user2_sk, user2_vk):
        from bigchaindb.common import crypto
        from bigchaindb.models import Transaction

        # create a new users
        user3_sk, user3_vk = crypto.generate_key_pair()
        user4_sk, user4_vk = crypto.generate_key_pair()

        tx_links = b.get_owned_ids(user_vk)
        inputs = sum([b.get_transaction(tx_link.txid).to_inputs() for tx_link
                      in tx_links], [])

        tx = Transaction.transfer(inputs, len(inputs) * [[user3_vk, user4_vk]])
        tx = tx.sign([user_sk, user2_sk])

        assert b.is_valid_transaction(tx) == tx
        assert len(tx.fulfillments) == len(inputs)
        assert len(tx.conditions) == len(inputs)

    def test_get_owned_ids_single_tx_single_output(self, b, user_sk, user_vk):
        from bigchaindb.common import crypto
        from bigchaindb.common.transaction import TransactionLink
        from bigchaindb.models import Transaction

        user2_sk, user2_vk = crypto.generate_key_pair()

        tx = Transaction.create([b.me], [user_vk])
        tx = tx.sign([b.me_private])
        block = b.create_block([tx])
        b.write_block(block, durability='hard')

        owned_inputs_user1 = b.get_owned_ids(user_vk)
        owned_inputs_user2 = b.get_owned_ids(user2_vk)
        assert owned_inputs_user1 == [TransactionLink(tx.id, 0)]
        assert owned_inputs_user2 == []

        tx = Transaction.transfer(tx.to_inputs(), [user2_vk], tx.asset)
        tx = tx.sign([user_sk])
        block = b.create_block([tx])
        b.write_block(block, durability='hard')

        owned_inputs_user1 = b.get_owned_ids(user_vk)
        owned_inputs_user2 = b.get_owned_ids(user2_vk)
        assert owned_inputs_user1 == []
        assert owned_inputs_user2 == [TransactionLink(tx.id, 0)]

    def test_get_owned_ids_single_tx_single_output_invalid_block(self, b,
                                                                 user_sk,
                                                                 user_vk):
        from bigchaindb.common import crypto
        from bigchaindb.common.transaction import TransactionLink
        from bigchaindb.models import Transaction

        genesis = b.create_genesis_block()
        user2_sk, user2_vk = crypto.generate_key_pair()

        tx = Transaction.create([b.me], [user_vk])
        tx = tx.sign([b.me_private])
        block = b.create_block([tx])
        b.write_block(block, durability='hard')

        # vote the block VALID
        vote = b.vote(block.id, genesis.id, True)
        b.write_vote(vote)

        owned_inputs_user1 = b.get_owned_ids(user_vk)
        owned_inputs_user2 = b.get_owned_ids(user2_vk)
        assert owned_inputs_user1 == [TransactionLink(tx.id, 0)]
        assert owned_inputs_user2 == []

        # NOTE: The transaction itself is valid, still will mark the block
        #       as invalid to mock the behavior.
        tx_invalid = Transaction.transfer(tx.to_inputs(), [user2_vk], tx.asset)
        tx_invalid = tx_invalid.sign([user_sk])
        block = b.create_block([tx_invalid])
        b.write_block(block, durability='hard')

        # vote the block invalid
        vote = b.vote(block.id, b.get_last_voted_block().id, False)
        b.write_vote(vote)

        owned_inputs_user1 = b.get_owned_ids(user_vk)
        owned_inputs_user2 = b.get_owned_ids(user2_vk)

        # should be the same as before (note tx, not tx_invalid)
        assert owned_inputs_user1 == [TransactionLink(tx.id, 0)]
        assert owned_inputs_user2 == []

    @pytest.mark.skipif(reason=('Multiple inputs are only allowed for the '
                                'same asset. Remove this after implementing ',
                                'multiple assets'))
    def test_get_owned_ids_single_tx_multiple_outputs(self, b, user_sk,
                                                      user_vk):
        import random
        from bigchaindb.common import crypto
        from bigchaindb.common.transaction import TransactionLink
        from bigchaindb.models import Transaction

        user2_sk, user2_vk = crypto.generate_key_pair()

        transactions = []
        for i in range(2):
            payload = {'somedata': random.randint(0, 255)}
            tx = Transaction.create([b.me], [user_vk], payload)
            tx = tx.sign([b.me_private])
            transactions.append(tx)
        block = b.create_block(transactions)
        b.write_block(block, durability='hard')

        # get input
        owned_inputs_user1 = b.get_owned_ids(user_vk)
        owned_inputs_user2 = b.get_owned_ids(user2_vk)

        expected_owned_inputs_user1 = [TransactionLink(tx.id, 0) for tx
                                       in transactions]
        assert owned_inputs_user1 == expected_owned_inputs_user1
        assert owned_inputs_user2 == []

        inputs = sum([tx.to_inputs() for tx in transactions], [])
        tx = Transaction.transfer(inputs, len(inputs) * [[user2_vk]])
        tx = tx.sign([user_sk])
        block = b.create_block([tx])
        b.write_block(block, durability='hard')

        owned_inputs_user1 = b.get_owned_ids(user_vk)
        owned_inputs_user2 = b.get_owned_ids(user2_vk)
        assert owned_inputs_user1 == []
        assert owned_inputs_user2 == [TransactionLink(tx.id, 0),
                                      TransactionLink(tx.id, 1)]

    def test_get_owned_ids_multiple_owners(self, b, user_sk, user_vk):
        from bigchaindb.common import crypto
        from bigchaindb.common.transaction import TransactionLink
        from bigchaindb.models import Transaction

        user2_sk, user2_vk = crypto.generate_key_pair()
        user3_sk, user3_vk = crypto.generate_key_pair()

        tx = Transaction.create([b.me], [user_vk, user2_vk])
        tx = tx.sign([b.me_private])
        block = b.create_block([tx])
        b.write_block(block, durability='hard')

        owned_inputs_user1 = b.get_owned_ids(user_vk)
        owned_inputs_user2 = b.get_owned_ids(user2_vk)
        expected_owned_inputs_user1 = [TransactionLink(tx.id, 0)]

        assert owned_inputs_user1 == owned_inputs_user2
        assert owned_inputs_user1 == expected_owned_inputs_user1

        tx = Transaction.transfer(tx.to_inputs(), [user3_vk], tx.asset)
        tx = tx.sign([user_sk, user2_sk])
        block = b.create_block([tx])
        b.write_block(block, durability='hard')

        owned_inputs_user1 = b.get_owned_ids(user_vk)
        owned_inputs_user2 = b.get_owned_ids(user2_vk)
        assert owned_inputs_user1 == owned_inputs_user2
        assert owned_inputs_user1 == []

    def test_get_spent_single_tx_single_output(self, b, user_sk, user_vk):
        from bigchaindb.common import crypto
        from bigchaindb.models import Transaction

        user2_sk, user2_vk = crypto.generate_key_pair()

        tx = Transaction.create([b.me], [user_vk])
        tx = tx.sign([b.me_private])
        block = b.create_block([tx])
        b.write_block(block, durability='hard')

        owned_inputs_user1 = b.get_owned_ids(user_vk).pop()

        # check spents
        input_txid = owned_inputs_user1.txid
        input_cid = owned_inputs_user1.cid
        spent_inputs_user1 = b.get_spent(input_txid, input_cid)
        assert spent_inputs_user1 is None

        # create a transaction and block
        tx = Transaction.transfer(tx.to_inputs(), [user2_vk], tx.asset)
        tx = tx.sign([user_sk])
        block = b.create_block([tx])
        b.write_block(block, durability='hard')

        spent_inputs_user1 = b.get_spent(input_txid, input_cid)
        assert spent_inputs_user1 == tx

    def test_get_spent_single_tx_single_output_invalid_block(self, b, user_sk, user_vk):
        from bigchaindb.common import crypto
        from bigchaindb.models import Transaction

        genesis = b.create_genesis_block()

        # create a new users
        user2_sk, user2_vk = crypto.generate_key_pair()

        tx = Transaction.create([b.me], [user_vk])
        tx = tx.sign([b.me_private])
        block = b.create_block([tx])
        b.write_block(block, durability='hard')

        # vote the block VALID
        vote = b.vote(block.id, genesis.id, True)
        b.write_vote(vote)

        owned_inputs_user1 = b.get_owned_ids(user_vk).pop()

        # check spents
        input_txid = owned_inputs_user1.txid
        input_cid = owned_inputs_user1.cid
        spent_inputs_user1 = b.get_spent(input_txid, input_cid)
        assert spent_inputs_user1 is None

        # create a transaction and block
        tx = Transaction.transfer(tx.to_inputs(), [user2_vk], tx.asset)
        tx = tx.sign([user_sk])
        block = b.create_block([tx])
        b.write_block(block, durability='hard')

        # vote the block invalid
        vote = b.vote(block.id, b.get_last_voted_block().id, False)
        b.write_vote(vote)
        # NOTE: I have no idea why this line is here
        b.get_transaction(tx.id)
        spent_inputs_user1 = b.get_spent(input_txid, input_cid)

        # Now there should be no spents (the block is invalid)
        assert spent_inputs_user1 is None

    @pytest.mark.skipif(reason=('Multiple inputs are only allowed for the '
                                'same asset. Remove this after implementing ',
                                'multiple assets'))
    def test_get_spent_single_tx_multiple_outputs(self, b, user_sk, user_vk):
        import random
        from bigchaindb.common import crypto
        from bigchaindb.models import Transaction

        # create a new users
        user2_sk, user2_vk = crypto.generate_key_pair()

        transactions = []
        for i in range(3):
            payload = {'somedata': random.randint(0, 255)}
            tx = Transaction.create([b.me], [user_vk], payload)
            tx = tx.sign([b.me_private])
            transactions.append(tx)
        block = b.create_block(transactions)
        b.write_block(block, durability='hard')

        owned_inputs_user1 = b.get_owned_ids(user_vk)

        # check spents
        for input_tx in owned_inputs_user1:
            assert b.get_spent(input_tx.txid, input_tx.cid) is None

        # select inputs to use
        inputs = sum([tx.to_inputs() for tx in transactions[:2]], [])

        # create a transaction and block
        tx = Transaction.transfer(inputs, len(inputs) * [[user2_vk]])
        tx = tx.sign([user_sk])
        block = b.create_block([tx])
        b.write_block(block, durability='hard')

        # check that used inputs are marked as spent
        for ffill in inputs:
            assert b.get_spent(ffill.tx_input.txid, ffill.tx_input.cid) == tx

        # check if remaining transaction that was unspent is also perceived
        # spendable by BigchainDB
        assert b.get_spent(transactions[2].id, 0) is None

    def test_get_spent_multiple_owners(self, b, user_sk, user_vk):
        import random
        from bigchaindb.common import crypto
        from bigchaindb.models import Transaction

        user2_sk, user2_vk = crypto.generate_key_pair()
        user3_sk, user3_vk = crypto.generate_key_pair()

        transactions = []
        for i in range(3):
            payload = {'somedata': random.randint(0, 255)}
            tx = Transaction.create([b.me], [user_vk, user2_vk], payload)
            tx = tx.sign([b.me_private])
            transactions.append(tx)
        block = b.create_block(transactions)
        b.write_block(block, durability='hard')

        owned_inputs_user1 = b.get_owned_ids(user_vk)

        # check spents
        for input_tx in owned_inputs_user1:
            assert b.get_spent(input_tx.txid, input_tx.cid) is None

        # create a transaction
        tx = Transaction.transfer(transactions[0].to_inputs(), [user3_vk], transactions[0].asset)
        tx = tx.sign([user_sk, user2_sk])
        block = b.create_block([tx])
        b.write_block(block, durability='hard')

        # check that used inputs are marked as spent
        assert b.get_spent(transactions[0].id, 0) == tx

        # check that the other remain marked as unspent
        for unspent in transactions[1:]:
            assert b.get_spent(unspent.id, 0) is None
