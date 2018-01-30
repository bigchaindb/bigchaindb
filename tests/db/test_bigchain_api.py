from time import sleep
from unittest.mock import patch

import pytest
from base58 import b58decode

pytestmark = pytest.mark.bdb


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
    tx = Transaction.create([b.me], [([b.me], 1)])
    tx = tx.sign([b.me_private])
    return tx


# TODO: Get rid of this and move to conftest
def dummy_block():
    import bigchaindb
    b = bigchaindb.Bigchain()
    block = b.create_block([dummy_tx()])
    return block


class TestBigchainApi(object):

    @pytest.mark.genesis
    def test_get_last_voted_block_cyclic_blockchain(self, b, monkeypatch):
        from bigchaindb.common.crypto import PrivateKey
        from bigchaindb.common.exceptions import CyclicBlockchainError
        from bigchaindb.common.utils import serialize
        from bigchaindb.models import Transaction

        tx = Transaction.create([b.me], [([b.me], 1)])
        tx = tx.sign([b.me_private])
        monkeypatch.setattr('time.time', lambda: 1)
        block1 = b.create_block([tx])
        b.write_block(block1)

        # Manipulate vote to create a cyclic Blockchain
        vote = b.vote(block1.id, b.get_last_voted_block().id, True)
        vote['vote']['previous_block'] = block1.id
        vote_data = serialize(vote['vote'])
        vote['signature'] = PrivateKey(b.me_private).sign(vote_data.encode())
        b.write_vote(vote)

        with pytest.raises(CyclicBlockchainError):
            b.get_last_voted_block()

    @pytest.mark.genesis
    def test_try_voting_while_constructing_cyclic_blockchain(self, b,
                                                             monkeypatch):
        from bigchaindb.common.exceptions import CyclicBlockchainError
        from bigchaindb.models import Transaction

        tx = Transaction.create([b.me], [([b.me], 1)])
        tx = tx.sign([b.me_private])
        block1 = b.create_block([tx])

        # We can simply submit twice the same block id and check if `Bigchain`
        # throws
        with pytest.raises(CyclicBlockchainError):
            b.vote(block1.id, block1.id, True)

    @pytest.mark.genesis
    def test_has_previous_vote_when_already_voted(self, b, monkeypatch):
        from bigchaindb.models import Transaction

        tx = Transaction.create([b.me], [([b.me], 1)])
        tx = tx.sign([b.me_private])

        monkeypatch.setattr('time.time', lambda: 1)
        block = b.create_block([tx])
        b.write_block(block)

        assert b.has_previous_vote(block.id) is False

        vote = b.vote(block.id, b.get_last_voted_block().id, True)
        b.write_vote(vote)

        assert b.has_previous_vote(block.id) is True

    @pytest.mark.genesis
    def test_get_spent_with_double_inclusion_detected(self, b, monkeypatch):
        from bigchaindb.exceptions import CriticalDoubleInclusion
        from bigchaindb.models import Transaction

        tx = Transaction.create([b.me], [([b.me], 1)])
        tx = tx.sign([b.me_private])

        monkeypatch.setattr('time.time', lambda: 1000000000)
        block1 = b.create_block([tx])
        b.write_block(block1)

        monkeypatch.setattr('time.time', lambda: 1000000020)
        transfer_tx = Transaction.transfer(tx.to_inputs(), [([b.me], 1)],
                                           asset_id=tx.id)
        transfer_tx = transfer_tx.sign([b.me_private])
        block2 = b.create_block([transfer_tx])
        b.write_block(block2)

        monkeypatch.setattr('time.time', lambda: 1000000030)
        transfer_tx2 = Transaction.transfer(tx.to_inputs(), [([b.me], 1)],
                                            asset_id=tx.id)
        transfer_tx2 = transfer_tx2.sign([b.me_private])
        block3 = b.create_block([transfer_tx2])
        b.write_block(block3)

        # Vote both block2 and block3 valid
        vote = b.vote(block2.id, b.get_last_voted_block().id, True)
        b.write_vote(vote)
        vote = b.vote(block3.id, b.get_last_voted_block().id, True)
        b.write_vote(vote)

        with pytest.raises(CriticalDoubleInclusion):
            b.get_spent(tx.id, 0)

    @pytest.mark.genesis
    def test_get_spent_with_double_spend_detected(self, b, monkeypatch):
        from bigchaindb.exceptions import CriticalDoubleSpend
        from bigchaindb.models import Transaction

        tx = Transaction.create([b.me], [([b.me], 1)])
        tx = tx.sign([b.me_private])

        monkeypatch.setattr('time.time', lambda: 1000000000)
        block1 = b.create_block([tx])
        b.write_block(block1)

        monkeypatch.setattr('time.time', lambda: 1000000020)
        transfer_tx = Transaction.transfer(tx.to_inputs(), [([b.me], 1)],
                                           asset_id=tx.id)
        transfer_tx = transfer_tx.sign([b.me_private])
        block2 = b.create_block([transfer_tx])
        b.write_block(block2)

        monkeypatch.setattr('time.time', lambda: 1000000030)
        transfer_tx2 = Transaction.transfer(tx.to_inputs(), [([b.me], 2)],
                                            asset_id=tx.id)
        transfer_tx2 = transfer_tx2.sign([b.me_private])
        block3 = b.create_block([transfer_tx2])
        b.write_block(block3)

        # Vote both block2 and block3 valid
        vote = b.vote(block2.id, b.get_last_voted_block().id, True)
        b.write_vote(vote)
        vote = b.vote(block3.id, b.get_last_voted_block().id, True)
        b.write_vote(vote)

        with pytest.raises(CriticalDoubleSpend):
            b.get_spent(tx.id, 0)

    @pytest.mark.genesis
    def test_get_block_status_for_tx_with_double_inclusion(self, b, monkeypatch):
        from bigchaindb.exceptions import CriticalDoubleInclusion
        from bigchaindb.models import Transaction

        tx = Transaction.create([b.me], [([b.me], 1)])
        tx = tx.sign([b.me_private])

        monkeypatch.setattr('time.time', lambda: 1000000000)
        block1 = b.create_block([tx])
        b.write_block(block1)

        monkeypatch.setattr('time.time', lambda: 1000000020)
        block2 = b.create_block([tx])
        b.write_block(block2)

        # Vote both blocks valid (creating a double spend)
        vote = b.vote(block1.id, b.get_last_voted_block().id, True)
        b.write_vote(vote)
        vote = b.vote(block2.id, b.get_last_voted_block().id, True)
        b.write_vote(vote)

        with pytest.raises(CriticalDoubleInclusion):
            b.get_blocks_status_containing_tx(tx.id)

    @pytest.mark.genesis
    def test_get_transaction_in_invalid_and_valid_block(self, monkeypatch, b):
        from bigchaindb.models import Transaction

        monkeypatch.setattr('time.time', lambda: 1000000000)
        tx1 = Transaction.create([b.me], [([b.me], 1)],
                                 metadata={'msg': 1})
        tx1 = tx1.sign([b.me_private])
        block1 = b.create_block([tx1])
        b.write_block(block1)

        monkeypatch.setattr('time.time', lambda: 1000000020)
        tx2 = Transaction.create([b.me], [([b.me], 1)],
                                 metadata={'msg': 2})
        tx2 = tx2.sign([b.me_private])
        block2 = b.create_block([tx2])
        b.write_block(block2)

        # vote the first block invalid
        vote = b.vote(block1.id, b.get_last_voted_block().id, False)
        b.write_vote(vote)

        # vote the second block valid
        vote = b.vote(block2.id, b.get_last_voted_block().id, True)
        b.write_vote(vote)

        assert b.get_transaction(tx1.id) is None
        assert b.get_transaction(tx2.id) == tx2

    @pytest.mark.genesis
    def test_text_search(self, b):
        from bigchaindb.models import Transaction
        from bigchaindb.backend.exceptions import OperationError
        from bigchaindb.backend.mongodb.connection import MongoDBConnection

        # define the assets
        asset1 = {'msg': 'BigchainDB 1'}
        asset2 = {'msg': 'BigchainDB 2'}
        asset3 = {'msg': 'BigchainDB 3'}

        # create the transactions
        tx1 = Transaction.create([b.me], [([b.me], 1)],
                                 asset=asset1).sign([b.me_private])
        tx2 = Transaction.create([b.me], [([b.me], 1)],
                                 asset=asset2).sign([b.me_private])
        tx3 = Transaction.create([b.me], [([b.me], 1)],
                                 asset=asset3).sign([b.me_private])

        # create the block
        block = b.create_block([tx1, tx2, tx3])
        b.write_block(block)

        # vote valid
        vote = b.vote(block.id, b.get_last_voted_block().id, True)
        b.write_vote(vote)

        # get the assets through text search
        # this query only works with MongoDB
        try:
            assets = list(b.text_search('bigchaindb'))
        except OperationError as exc:
            assert not isinstance(b.connection, MongoDBConnection)
        else:
            assert len(assets) == 3

    @pytest.mark.genesis
    def test_text_search_returns_valid_only(self, monkeypatch, b):
        from bigchaindb.models import Transaction
        from bigchaindb.backend.exceptions import OperationError
        from bigchaindb.backend.mongodb.connection import MongoDBConnection

        asset_valid = {'msg': 'Hello BigchainDB!'}
        asset_invalid = {'msg': 'Goodbye BigchainDB!'}

        monkeypatch.setattr('time.time', lambda: 1000000000)
        tx1 = Transaction.create([b.me], [([b.me], 1)],
                                 asset=asset_valid)
        tx1 = tx1.sign([b.me_private])
        block1 = b.create_block([tx1])
        b.write_block(block1)

        monkeypatch.setattr('time.time', lambda: 1000000020)
        tx2 = Transaction.create([b.me], [([b.me], 1)],
                                 asset=asset_invalid)
        tx2 = tx2.sign([b.me_private])
        block2 = b.create_block([tx2])
        b.write_block(block2)

        # vote the first block valid
        vote = b.vote(block1.id, b.get_last_voted_block().id, True)
        b.write_vote(vote)

        # vote the second block invalid
        vote = b.vote(block2.id, b.get_last_voted_block().id, False)
        b.write_vote(vote)

        # get assets with text search
        try:
            assets = list(b.text_search('bigchaindb'))
        except OperationError:
            assert not isinstance(b.connection, MongoDBConnection)
            return

        # should only return one asset
        assert len(assets) == 1
        # should return the asset created by tx1
        assert assets[0] == {
            'data': {'msg': 'Hello BigchainDB!'},
            'id': tx1.id
        }

    @pytest.mark.usefixtures('inputs')
    def test_write_transaction(self, b, user_pk, user_sk):
        from bigchaindb import Bigchain
        from bigchaindb.models import Transaction

        input_tx = b.get_owned_ids(user_pk).pop()
        input_tx = b.get_transaction(input_tx.txid)
        inputs = input_tx.to_inputs()
        tx = Transaction.transfer(inputs, [([user_pk], 1)],
                                  asset_id=input_tx.id)
        tx = tx.sign([user_sk])
        b.write_transaction(tx)

        tx_from_db, status = b.get_transaction(tx.id, include_status=True)

        assert tx_from_db.to_dict() == tx.to_dict()
        assert status == Bigchain.TX_IN_BACKLOG

    @pytest.mark.usefixtures('inputs')
    def test_read_transaction(self, b, user_pk, user_sk):
        from bigchaindb.models import Transaction

        input_tx = b.get_owned_ids(user_pk).pop()
        input_tx = b.get_transaction(input_tx.txid)
        inputs = input_tx.to_inputs()
        tx = Transaction.transfer(inputs, [([user_pk], 1)],
                                  asset_id=input_tx.id)
        tx = tx.sign([user_sk])
        b.write_transaction(tx)

        # create block and write it to the bighcain before retrieving the transaction
        block = b.create_block([tx])
        b.write_block(block)

        response, status = b.get_transaction(tx.id, include_status=True)
        # add validity information, which will be returned
        assert tx.to_dict() == response.to_dict()
        assert status == b.TX_UNDECIDED

    @pytest.mark.usefixtures('inputs')
    def test_read_transaction_invalid_block(self, b, user_pk, user_sk):
        from bigchaindb.models import Transaction

        input_tx = b.get_owned_ids(user_pk).pop()
        input_tx = b.get_transaction(input_tx.txid)
        inputs = input_tx.to_inputs()
        tx = Transaction.transfer(inputs, [([user_pk], 1)],
                                  asset_id=input_tx.id)
        tx = tx.sign([user_sk])
        # There's no need to b.write_transaction(tx) to the backlog

        # create block
        block = b.create_block([tx])
        b.write_block(block)

        # vote the block invalid
        vote = b.vote(block.id, b.get_last_voted_block().id, False)
        b.write_vote(vote)
        response = b.get_transaction(tx.id)

        # should be None, because invalid blocks are ignored
        # and a copy of the tx is not in the backlog
        assert response is None

    @pytest.mark.usefixtures('inputs')
    def test_read_transaction_invalid_block_and_backlog(self, b, user_pk, user_sk):
        from bigchaindb.models import Transaction

        input_tx = b.get_owned_ids(user_pk).pop()
        input_tx = b.get_transaction(input_tx.txid)
        inputs = input_tx.to_inputs()
        tx = Transaction.transfer(inputs, [([user_pk], 1)],
                                  asset_id=input_tx.id)
        tx = tx.sign([user_sk])

        # Make sure there's a copy of tx in the backlog
        b.write_transaction(tx)

        # create block
        block = b.create_block([tx])
        b.write_block(block)

        # vote the block invalid
        vote = b.vote(block.id, b.get_last_voted_block().id, False)
        b.write_vote(vote)

        # a copy of the tx is both in the backlog and in an invalid
        # block, so get_transaction should return a transaction,
        # and a status of TX_IN_BACKLOG
        response, status = b.get_transaction(tx.id, include_status=True)
        assert tx.to_dict() == response.to_dict()
        assert status == b.TX_IN_BACKLOG

    @pytest.mark.usefixtures('inputs')
    def test_genesis_block(self, b):
        from bigchaindb.backend import query
        block = query.get_genesis_block(b.connection)

        assert len(block['block']['transactions']) == 1
        assert block['block']['transactions'][0]['operation'] == 'GENESIS'
        assert block['block']['transactions'][0]['inputs'][0]['fulfills'] is None

    @pytest.mark.genesis
    def test_create_genesis_block_fails_if_table_not_empty(self, b):
        from bigchaindb.common.exceptions import GenesisBlockAlreadyExistsError

        with pytest.raises(GenesisBlockAlreadyExistsError):
            b.create_genesis_block()

    @pytest.mark.skipif(reason='This test may not make sense after changing the chainification mode')
    def test_get_last_block(self, b):
        from bigchaindb.backend import query
        # get the number of blocks
        num_blocks = query.count_blocks(b.connection)

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
        b.write_block(new_block)

        prev_block = b.get_previous_block(new_block)

        assert prev_block == last_block

    @pytest.mark.skipif(reason='This test may not make sense after changing the chainification mode')
    def test_get_previous_block_id(self, b):
        last_block = b.get_last_block()
        new_block = b.create_block([])
        b.write_block(new_block)

        prev_block_id = b.get_previous_block_id(new_block)

        assert prev_block_id == last_block['id']

    def test_create_empty_block(self, b):
        from bigchaindb.common.exceptions import OperationError

        with pytest.raises(OperationError) as excinfo:
            b.create_block([])

        assert excinfo.value.args[0] == 'Empty block creation is not allowed'

    @pytest.mark.usefixtures('inputs')
    def test_get_block_by_id(self, b):
        new_block = dummy_block()
        b.write_block(new_block)

        assert b.get_block(new_block.id) == new_block.to_dict()
        block, status = b.get_block(new_block.id, include_status=True)
        assert status == b.BLOCK_UNDECIDED

    @pytest.mark.genesis
    def test_get_last_voted_block_returns_genesis_if_no_votes_has_been_casted(self, b):
        from bigchaindb.models import Block
        from bigchaindb.backend import query

        genesis = query.get_genesis_block(b.connection)
        genesis = Block.from_db(b, genesis)
        gb = b.get_last_voted_block()
        assert gb == genesis
        assert b.validate_block(gb) == gb

    def test_get_last_voted_block_returns_the_correct_block_same_timestamp(self,
                                                                           b,
                                                                           monkeypatch,
                                                                           genesis_block):
        assert b.get_last_voted_block() == genesis_block

        monkeypatch.setattr('time.time', lambda: 1)
        block_1 = dummy_block()
        monkeypatch.setattr('time.time', lambda: 2)
        block_2 = dummy_block()
        monkeypatch.setattr('time.time', lambda: 3)
        block_3 = dummy_block()

        b.write_block(block_1)
        b.write_block(block_2)
        b.write_block(block_3)

        # make sure all the votes are written with the same timestamps
        monkeypatch.setattr('time.time', lambda: 4)
        b.write_vote(b.vote(block_1.id, b.get_last_voted_block().id, True))
        assert b.get_last_voted_block().id == block_1.id

        b.write_vote(b.vote(block_2.id, b.get_last_voted_block().id, True))
        assert b.get_last_voted_block().id == block_2.id

        b.write_vote(b.vote(block_3.id, b.get_last_voted_block().id, True))
        assert b.get_last_voted_block().id == block_3.id

    def test_get_last_voted_block_returns_the_correct_block_different_timestamps(self,
                                                                                 b,
                                                                                 monkeypatch,
                                                                                 genesis_block):
        assert b.get_last_voted_block() == genesis_block

        monkeypatch.setattr('time.time', lambda: 1)
        block_1 = dummy_block()
        monkeypatch.setattr('time.time', lambda: 2)
        block_2 = dummy_block()
        monkeypatch.setattr('time.time', lambda: 3)
        block_3 = dummy_block()

        b.write_block(block_1)
        b.write_block(block_2)
        b.write_block(block_3)

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

    @pytest.mark.usefixtures('inputs')
    def test_assign_transaction_one_node(self, b, user_pk, user_sk):
        from bigchaindb.backend import query
        from bigchaindb.models import Transaction

        input_tx = b.get_owned_ids(user_pk).pop()
        input_tx = b.get_transaction(input_tx.txid)
        inputs = input_tx.to_inputs()
        tx = Transaction.transfer(inputs, [([user_pk], 1)],
                                  asset_id=input_tx.id)
        tx = tx.sign([user_sk])
        b.write_transaction(tx)

        # retrieve the transaction
        response = list(query.get_stale_transactions(b.connection, 0))[0]

        # check if the assignee is the current node
        assert response['assignee'] == b.me

    @pytest.mark.usefixtures('inputs')
    def test_assign_transaction_multiple_nodes(self, b, user_pk, user_sk):
        from bigchaindb.backend import query
        from bigchaindb.common.crypto import generate_key_pair
        from bigchaindb.models import Transaction

        # create 5 federation nodes
        for _ in range(5):
            b.nodes_except_me.append(generate_key_pair()[1])

        # test assignee for several transactions
        for i in range(20):
            input_tx = b.get_owned_ids(user_pk).pop()
            input_tx = b.get_transaction(input_tx.txid)
            inputs = input_tx.to_inputs()
            tx = Transaction.transfer(inputs, [([user_pk], 1)],
                                      asset_id=input_tx.id,
                                      metadata={'msg': i})
            tx = tx.sign([user_sk])
            b.write_transaction(tx)

        # retrieve the transaction
        response = query.get_stale_transactions(b.connection, 0)

        # check if the assignee is one of the _other_ federation nodes
        for tx in response:
            assert tx['assignee'] in b.nodes_except_me

    @pytest.mark.usefixtures('inputs')
    def test_non_create_input_not_found(self, b, user_pk):
        from cryptoconditions import Ed25519Sha256
        from bigchaindb.common.exceptions import InputDoesNotExist
        from bigchaindb.common.transaction import Input, TransactionLink
        from bigchaindb.models import Transaction
        from bigchaindb import Bigchain

        # Create an input for a non existing transaction
        input = Input(Ed25519Sha256(public_key=b58decode(user_pk)),
                      [user_pk],
                      TransactionLink('somethingsomething', 0))
        tx = Transaction.transfer([input], [([user_pk], 1)],
                                  asset_id='mock_asset_link')

        with pytest.raises(InputDoesNotExist):
            tx.validate(Bigchain())

    def test_count_backlog(self, b, user_pk):
        from bigchaindb.backend import query
        from bigchaindb.models import Transaction

        for i in range(4):
            tx = Transaction.create([b.me], [([user_pk], 1)],
                                    metadata={'msg': i}) \
                            .sign([b.me_private])
            b.write_transaction(tx)

        assert query.count_backlog(b.connection) == 4


class TestTransactionValidation(object):
    def test_non_create_input_not_found(self, b, user_pk, signed_transfer_tx):
        from bigchaindb.common.exceptions import InputDoesNotExist
        from bigchaindb.common.transaction import TransactionLink

        signed_transfer_tx.inputs[0].fulfills = TransactionLink('c', 0)
        with pytest.raises(InputDoesNotExist):
            b.validate_transaction(signed_transfer_tx)

    @pytest.mark.usefixtures('inputs')
    def test_non_create_valid_input_wrong_owner(self, b, user_pk):
        from bigchaindb.common.crypto import generate_key_pair
        from bigchaindb.common.exceptions import InvalidSignature
        from bigchaindb.models import Transaction

        input_tx = b.get_owned_ids(user_pk).pop()
        input_transaction = b.get_transaction(input_tx.txid)
        sk, pk = generate_key_pair()
        tx = Transaction.create([pk], [([user_pk], 1)])
        tx.operation = 'TRANSFER'
        tx.asset = {'id': input_transaction.id}
        tx.inputs[0].fulfills = input_tx

        with pytest.raises(InvalidSignature):
            b.validate_transaction(tx)

    @pytest.mark.usefixtures('inputs')
    def test_non_create_double_spend(self, b, signed_create_tx,
                                     signed_transfer_tx, double_spend_tx):
        from bigchaindb.common.exceptions import DoubleSpend

        block1 = b.create_block([signed_create_tx])
        b.write_block(block1)

        # vote block valid
        vote = b.vote(block1.id, b.get_last_voted_block().id, True)
        b.write_vote(vote)

        b.write_transaction(signed_transfer_tx)
        block = b.create_block([signed_transfer_tx])
        b.write_block(block)

        # vote block valid
        vote = b.vote(block.id, b.get_last_voted_block().id, True)
        b.write_vote(vote)

        sleep(1)

        with pytest.raises(DoubleSpend):
            b.validate_transaction(double_spend_tx)

    @pytest.mark.usefixtures('inputs')
    def test_valid_non_create_transaction_after_block_creation(self, b,
                                                               user_pk,
                                                               user_sk):
        from bigchaindb.models import Transaction

        input_tx = b.get_owned_ids(user_pk).pop()
        input_tx = b.get_transaction(input_tx.txid)
        inputs = input_tx.to_inputs()
        transfer_tx = Transaction.transfer(inputs, [([user_pk], 1)],
                                           asset_id=input_tx.id)
        transfer_tx = transfer_tx.sign([user_sk])

        assert transfer_tx == b.validate_transaction(transfer_tx)

        # create block
        block = b.create_block([transfer_tx])
        assert b.validate_block(block) == block
        b.write_block(block)

        # check that the transaction is still valid after being written to the
        # bigchain
        assert transfer_tx == b.validate_transaction(transfer_tx)

    @pytest.mark.usefixtures('inputs')
    def test_transaction_not_in_valid_block(self, b, user_pk, user_sk):
        from bigchaindb.models import Transaction
        from bigchaindb.common.exceptions import TransactionNotInValidBlock

        input_tx = b.get_owned_ids(user_pk).pop()
        input_tx = b.get_transaction(input_tx.txid)
        inputs = input_tx.to_inputs()

        # create a transaction that's valid but not in a voted valid block
        transfer_tx = Transaction.transfer(inputs, [([user_pk], 1)],
                                           asset_id=input_tx.id)
        transfer_tx = transfer_tx.sign([user_sk])

        assert transfer_tx == b.validate_transaction(transfer_tx)

        # create block
        block = b.create_block([transfer_tx])
        b.write_block(block)

        # create transaction with the undecided input
        tx_invalid = Transaction.transfer(transfer_tx.to_inputs(),
                                          [([user_pk], 1)],
                                          asset_id=transfer_tx.asset['id'])
        tx_invalid = tx_invalid.sign([user_sk])

        with pytest.raises(TransactionNotInValidBlock):
            b.validate_transaction(tx_invalid)


class TestBlockValidation(object):
    @pytest.mark.skipif(reason='Separated tx validation from block creation.')
    @pytest.mark.usefixtures('inputs')
    def test_invalid_transactions_in_block(self, b, user_pk):
        from bigchaindb import utils
        from bigchaindb.common import crypto
        from bigchaindb.common.exceptions import TransactionOwnerError
        from bigchaindb.common.utils import gen_timestamp

        # invalid transaction
        valid_input = b.get_owned_ids(user_pk).pop()
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
        block_data = utils.serialize_block(block)
        block_hash = crypto.hash_data(block_data)
        block_signature = crypto.PrivateKey(b.me_private).sign(block_data)

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
        block.signature = crypto.PrivateKey(b.me_private).sign(b'wrongdata')

        # check that validate_block raises an InvalidSignature exception
        with pytest.raises(InvalidSignature):
            b.validate_block(block)

    def test_invalid_node_pubkey(self, b):
        from bigchaindb.common.exceptions import SybilError
        from bigchaindb.common import crypto

        # blocks can only be created by a federation node
        # create a valid block
        block = dummy_block()

        # create some temp keys
        tmp_sk, tmp_pk = crypto.generate_key_pair()

        # change the block node_pubkey
        block.node_pubkey = tmp_pk

        # just to make sure lets re-hash the block and create a valid signature
        # from a non federation node
        block = block.sign(tmp_sk)

        # check that validate_block raises an SybilError
        with pytest.raises(SybilError):
            b.validate_block(block)


class TestMultipleInputs(object):
    def test_transfer_single_owner_single_input(self, b, inputs, user_pk,
                                                user_sk):
        from bigchaindb.common import crypto
        from bigchaindb.models import Transaction
        user2_sk, user2_pk = crypto.generate_key_pair()

        tx_link = b.get_owned_ids(user_pk).pop()
        input_tx = b.get_transaction(tx_link.txid)
        inputs = input_tx.to_inputs()
        tx = Transaction.transfer(inputs, [([user2_pk], 1)],
                                  asset_id=input_tx.id)
        tx = tx.sign([user_sk])

        # validate transaction
        tx.validate(b)
        assert len(tx.inputs) == 1
        assert len(tx.outputs) == 1

    def test_single_owner_before_multiple_owners_after_single_input(self, b,
                                                                    user_sk,
                                                                    user_pk,
                                                                    inputs):
        from bigchaindb.common import crypto
        from bigchaindb.models import Transaction

        user2_sk, user2_pk = crypto.generate_key_pair()
        user3_sk, user3_pk = crypto.generate_key_pair()

        owned_inputs = b.get_owned_ids(user_pk)
        tx_link = owned_inputs.pop()
        input_tx = b.get_transaction(tx_link.txid)
        tx = Transaction.transfer(input_tx.to_inputs(),
                                  [([user2_pk, user3_pk], 1)],
                                  asset_id=input_tx.id)
        tx = tx.sign([user_sk])

        tx.validate(b)
        assert len(tx.inputs) == 1
        assert len(tx.outputs) == 1

    @pytest.mark.usefixtures('inputs')
    def test_multiple_owners_before_single_owner_after_single_input(self, b,
                                                                    user_sk,
                                                                    user_pk):
        from bigchaindb.common import crypto
        from bigchaindb.models import Transaction

        user2_sk, user2_pk = crypto.generate_key_pair()
        user3_sk, user3_pk = crypto.generate_key_pair()

        tx = Transaction.create([b.me], [([user_pk, user2_pk], 1)])
        tx = tx.sign([b.me_private])
        block = b.create_block([tx])
        b.write_block(block)

        # vote block valid
        vote = b.vote(block.id, b.get_last_voted_block().id, True)
        b.write_vote(vote)

        owned_input = b.get_owned_ids(user_pk).pop()
        input_tx = b.get_transaction(owned_input.txid)
        inputs = input_tx.to_inputs()

        transfer_tx = Transaction.transfer(inputs, [([user3_pk], 1)],
                                           asset_id=input_tx.id)
        transfer_tx = transfer_tx.sign([user_sk, user2_sk])

        # validate transaction
        transfer_tx.validate(b)
        assert len(transfer_tx.inputs) == 1
        assert len(transfer_tx.outputs) == 1

    @pytest.mark.usefixtures('inputs')
    def test_multiple_owners_before_multiple_owners_after_single_input(self, b,
                                                                       user_sk,
                                                                       user_pk):
        from bigchaindb.common import crypto
        from bigchaindb.models import Transaction

        user2_sk, user2_pk = crypto.generate_key_pair()
        user3_sk, user3_pk = crypto.generate_key_pair()
        user4_sk, user4_pk = crypto.generate_key_pair()

        tx = Transaction.create([b.me], [([user_pk, user2_pk], 1)])
        tx = tx.sign([b.me_private])
        block = b.create_block([tx])
        b.write_block(block)

        # vote block valid
        vote = b.vote(block.id, b.get_last_voted_block().id, True)
        b.write_vote(vote)

        # get input
        tx_link = b.get_owned_ids(user_pk).pop()
        tx_input = b.get_transaction(tx_link.txid)

        tx = Transaction.transfer(tx_input.to_inputs(),
                                  [([user3_pk, user4_pk], 1)],
                                  asset_id=tx_input.id)
        tx = tx.sign([user_sk, user2_sk])

        tx.validate(b)
        assert len(tx.inputs) == 1
        assert len(tx.outputs) == 1

    def test_get_owned_ids_single_tx_single_output(self, b, user_sk, user_pk):
        from bigchaindb.common import crypto
        from bigchaindb.common.transaction import TransactionLink
        from bigchaindb.models import Transaction

        user2_sk, user2_pk = crypto.generate_key_pair()

        tx = Transaction.create([b.me], [([user_pk], 1)])
        tx = tx.sign([b.me_private])
        block = b.create_block([tx])
        b.write_block(block)

        owned_inputs_user1 = b.get_owned_ids(user_pk)
        owned_inputs_user2 = b.get_owned_ids(user2_pk)
        assert owned_inputs_user1 == [TransactionLink(tx.id, 0)]
        assert owned_inputs_user2 == []

        tx = Transaction.transfer(tx.to_inputs(), [([user2_pk], 1)],
                                  asset_id=tx.id)
        tx = tx.sign([user_sk])
        block = b.create_block([tx])
        b.write_block(block)

        owned_inputs_user1 = b.get_owned_ids(user_pk)
        owned_inputs_user2 = b.get_owned_ids(user2_pk)
        assert owned_inputs_user1 == []
        assert owned_inputs_user2 == [TransactionLink(tx.id, 0)]

    def test_get_owned_ids_single_tx_single_output_invalid_block(self, b,
                                                                 user_sk,
                                                                 user_pk,
                                                                 genesis_block):
        from bigchaindb.common import crypto
        from bigchaindb.common.transaction import TransactionLink
        from bigchaindb.models import Transaction

        user2_sk, user2_pk = crypto.generate_key_pair()

        tx = Transaction.create([b.me], [([user_pk], 1)])
        tx = tx.sign([b.me_private])
        block = b.create_block([tx])
        b.write_block(block)

        # vote the block VALID
        vote = b.vote(block.id, genesis_block.id, True)
        b.write_vote(vote)

        owned_inputs_user1 = b.get_owned_ids(user_pk)
        owned_inputs_user2 = b.get_owned_ids(user2_pk)
        assert owned_inputs_user1 == [TransactionLink(tx.id, 0)]
        assert owned_inputs_user2 == []

        # NOTE: The transaction itself is valid, still will mark the block
        #       as invalid to mock the behavior.
        tx_invalid = Transaction.transfer(tx.to_inputs(), [([user2_pk], 1)],
                                          asset_id=tx.id)
        tx_invalid = tx_invalid.sign([user_sk])
        block = b.create_block([tx_invalid])
        b.write_block(block)

        # vote the block invalid
        vote = b.vote(block.id, b.get_last_voted_block().id, False)
        b.write_vote(vote)

        owned_inputs_user1 = b.get_owned_ids(user_pk)
        owned_inputs_user2 = b.get_owned_ids(user2_pk)

        # should be the same as before (note tx, not tx_invalid)
        assert owned_inputs_user1 == [TransactionLink(tx.id, 0)]
        assert owned_inputs_user2 == []

    def test_get_owned_ids_single_tx_multiple_outputs(self, b, user_sk,
                                                      user_pk):
        from bigchaindb.common import crypto
        from bigchaindb.common.transaction import TransactionLink
        from bigchaindb.models import Transaction

        user2_sk, user2_pk = crypto.generate_key_pair()

        # create divisible asset
        tx_create = Transaction.create([b.me], [([user_pk], 1), ([user_pk], 1)])
        tx_create_signed = tx_create.sign([b.me_private])
        block = b.create_block([tx_create_signed])
        b.write_block(block)

        # get input
        owned_inputs_user1 = b.get_owned_ids(user_pk)
        owned_inputs_user2 = b.get_owned_ids(user2_pk)

        expected_owned_inputs_user1 = [TransactionLink(tx_create.id, 0),
                                       TransactionLink(tx_create.id, 1)]
        assert owned_inputs_user1 == expected_owned_inputs_user1
        assert owned_inputs_user2 == []

        # transfer divisible asset divided in two outputs
        tx_transfer = Transaction.transfer(tx_create.to_inputs(),
                                           [([user2_pk], 1), ([user2_pk], 1)],
                                           asset_id=tx_create.id)
        tx_transfer_signed = tx_transfer.sign([user_sk])
        block = b.create_block([tx_transfer_signed])
        b.write_block(block)

        owned_inputs_user1 = b.get_owned_ids(user_pk)
        owned_inputs_user2 = b.get_owned_ids(user2_pk)
        assert owned_inputs_user1 == []
        assert owned_inputs_user2 == [TransactionLink(tx_transfer.id, 0),
                                      TransactionLink(tx_transfer.id, 1)]

    def test_get_owned_ids_multiple_owners(self, b, user_sk, user_pk):
        from bigchaindb.common import crypto
        from bigchaindb.common.transaction import TransactionLink
        from bigchaindb.models import Transaction

        user2_sk, user2_pk = crypto.generate_key_pair()
        user3_sk, user3_pk = crypto.generate_key_pair()

        tx = Transaction.create([b.me], [([user_pk, user2_pk], 1)])
        tx = tx.sign([b.me_private])
        block = b.create_block([tx])
        b.write_block(block)

        owned_inputs_user1 = b.get_owned_ids(user_pk)
        owned_inputs_user2 = b.get_owned_ids(user2_pk)
        expected_owned_inputs_user1 = [TransactionLink(tx.id, 0)]

        assert owned_inputs_user1 == owned_inputs_user2
        assert owned_inputs_user1 == expected_owned_inputs_user1

        tx = Transaction.transfer(tx.to_inputs(), [([user3_pk], 1)],
                                  asset_id=tx.id)
        tx = tx.sign([user_sk, user2_sk])
        block = b.create_block([tx])
        b.write_block(block)

        owned_inputs_user1 = b.get_owned_ids(user_pk)
        owned_inputs_user2 = b.get_owned_ids(user2_pk)
        assert owned_inputs_user1 == owned_inputs_user2
        assert owned_inputs_user1 == []

    def test_get_spent_single_tx_single_output(self, b, user_sk, user_pk):
        from bigchaindb.common import crypto
        from bigchaindb.models import Transaction

        user2_sk, user2_pk = crypto.generate_key_pair()

        tx = Transaction.create([b.me], [([user_pk], 1)])
        tx = tx.sign([b.me_private])
        block = b.create_block([tx])
        b.write_block(block)

        owned_inputs_user1 = b.get_owned_ids(user_pk).pop()

        # check spents
        input_txid = owned_inputs_user1.txid
        input_idx = owned_inputs_user1.output
        spent_inputs_user1 = b.get_spent(input_txid, input_idx)
        assert spent_inputs_user1 is None

        # create a transaction and block
        tx = Transaction.transfer(tx.to_inputs(), [([user2_pk], 1)],
                                  asset_id=tx.id)
        tx = tx.sign([user_sk])
        block = b.create_block([tx])
        b.write_block(block)

        spent_inputs_user1 = b.get_spent(input_txid, input_idx)
        assert spent_inputs_user1 == tx

    def test_get_spent_single_tx_single_output_invalid_block(self, b,
                                                             user_sk,
                                                             user_pk,
                                                             genesis_block):
        from bigchaindb.common import crypto
        from bigchaindb.models import Transaction

        # create a new users
        user2_sk, user2_pk = crypto.generate_key_pair()

        tx = Transaction.create([b.me], [([user_pk], 1)])
        tx = tx.sign([b.me_private])
        block = b.create_block([tx])
        b.write_block(block)

        # vote the block VALID
        vote = b.vote(block.id, genesis_block.id, True)
        b.write_vote(vote)

        owned_inputs_user1 = b.get_owned_ids(user_pk).pop()

        # check spents
        input_txid = owned_inputs_user1.txid
        input_idx = owned_inputs_user1.output
        spent_inputs_user1 = b.get_spent(input_txid, input_idx)
        assert spent_inputs_user1 is None

        # create a transaction and block
        tx = Transaction.transfer(tx.to_inputs(), [([user2_pk], 1)],
                                  asset_id=tx.id)
        tx = tx.sign([user_sk])
        block = b.create_block([tx])
        b.write_block(block)

        # vote the block invalid
        vote = b.vote(block.id, b.get_last_voted_block().id, False)
        b.write_vote(vote)
        # NOTE: I have no idea why this line is here
        b.get_transaction(tx.id)
        spent_inputs_user1 = b.get_spent(input_txid, input_idx)

        # Now there should be no spents (the block is invalid)
        assert spent_inputs_user1 is None

    def test_get_spent_single_tx_multiple_outputs(self, b, user_sk, user_pk):
        from bigchaindb.common import crypto
        from bigchaindb.models import Transaction

        # create a new users
        user2_sk, user2_pk = crypto.generate_key_pair()

        # create a divisible asset with 3 outputs
        tx_create = Transaction.create([b.me],
                                       [([user_pk], 1),
                                        ([user_pk], 1),
                                        ([user_pk], 1)])
        tx_create_signed = tx_create.sign([b.me_private])
        block = b.create_block([tx_create_signed])
        b.write_block(block)

        owned_inputs_user1 = b.get_owned_ids(user_pk)

        # check spents
        for input_tx in owned_inputs_user1:
            assert b.get_spent(input_tx.txid, input_tx.output) is None

        # transfer the first 2 inputs
        tx_transfer = Transaction.transfer(tx_create.to_inputs()[:2],
                                           [([user2_pk], 1), ([user2_pk], 1)],
                                           asset_id=tx_create.id)
        tx_transfer_signed = tx_transfer.sign([user_sk])
        block = b.create_block([tx_transfer_signed])
        b.write_block(block)

        # check that used inputs are marked as spent
        for ffill in tx_create.to_inputs()[:2]:
            spent_tx = b.get_spent(ffill.fulfills.txid, ffill.fulfills.output)
            assert spent_tx == tx_transfer_signed

        # check if remaining transaction that was unspent is also perceived
        # spendable by BigchainDB
        assert b.get_spent(tx_create.to_inputs()[2].fulfills.txid, 2) is None

    def test_get_spent_multiple_owners(self, b, user_sk, user_pk):
        from bigchaindb.common import crypto
        from bigchaindb.models import Transaction

        user2_sk, user2_pk = crypto.generate_key_pair()
        user3_sk, user3_pk = crypto.generate_key_pair()

        transactions = []
        for i in range(3):
            payload = {'somedata': i}
            tx = Transaction.create([b.me], [([user_pk, user2_pk], 1)],
                                    payload)
            tx = tx.sign([b.me_private])
            transactions.append(tx)
        block = b.create_block(transactions)
        b.write_block(block)

        owned_inputs_user1 = b.get_owned_ids(user_pk)

        # check spents
        for input_tx in owned_inputs_user1:
            assert b.get_spent(input_tx.txid, input_tx.output) is None

        # create a transaction
        tx = Transaction.transfer(transactions[0].to_inputs(),
                                  [([user3_pk], 1)],
                                  asset_id=transactions[0].id)
        tx = tx.sign([user_sk, user2_sk])
        block = b.create_block([tx])
        b.write_block(block)

        # check that used inputs are marked as spent
        assert b.get_spent(transactions[0].id, 0) == tx

        # check that the other remain marked as unspent
        for unspent in transactions[1:]:
            assert b.get_spent(unspent.id, 0) is None


def test_get_owned_ids_calls_get_outputs_filtered():
    from bigchaindb.core import Bigchain
    with patch('bigchaindb.core.Bigchain.get_outputs_filtered') as gof:
        b = Bigchain()
        res = b.get_owned_ids('abc')
    gof.assert_called_once_with('abc', spent=False)
    assert res == gof()


def test_get_outputs_filtered_only_unspent():
    from bigchaindb.common.transaction import TransactionLink
    from bigchaindb.core import Bigchain
    with patch('bigchaindb.fastquery.FastQuery.get_outputs_by_public_key') as get_outputs:
        get_outputs.return_value = [TransactionLink('a', 1),
                                    TransactionLink('b', 2)]
        with patch('bigchaindb.fastquery.FastQuery.filter_spent_outputs') as filter_spent:
            filter_spent.return_value = [TransactionLink('b', 2)]
            out = Bigchain().get_outputs_filtered('abc', spent=False)
    get_outputs.assert_called_once_with('abc')
    assert out == [TransactionLink('b', 2)]


def test_get_outputs_filtered_only_spent():
    from bigchaindb.common.transaction import TransactionLink
    from bigchaindb.core import Bigchain
    with patch('bigchaindb.fastquery.FastQuery.get_outputs_by_public_key') as get_outputs:
        get_outputs.return_value = [TransactionLink('a', 1),
                                    TransactionLink('b', 2)]
        with patch('bigchaindb.fastquery.FastQuery.filter_unspent_outputs') as filter_spent:
            filter_spent.return_value = [TransactionLink('b', 2)]
            out = Bigchain().get_outputs_filtered('abc', spent=True)
    get_outputs.assert_called_once_with('abc')
    assert out == [TransactionLink('b', 2)]


@patch('bigchaindb.fastquery.FastQuery.filter_unspent_outputs')
@patch('bigchaindb.fastquery.FastQuery.filter_spent_outputs')
def test_get_outputs_filtered(filter_spent, filter_unspent):
    from bigchaindb.common.transaction import TransactionLink
    from bigchaindb.core import Bigchain
    with patch('bigchaindb.fastquery.FastQuery.get_outputs_by_public_key') as get_outputs:
        get_outputs.return_value = [TransactionLink('a', 1),
                                    TransactionLink('b', 2)]
        out = Bigchain().get_outputs_filtered('abc')
    get_outputs.assert_called_once_with('abc')
    filter_spent.assert_not_called()
    filter_unspent.assert_not_called()
    assert out == get_outputs.return_value


@pytest.mark.bdb
def test_cant_spend_same_input_twice_in_tx(b, genesis_block):
    """Recreate duplicated fulfillments bug
    https://github.com/bigchaindb/bigchaindb/issues/1099
    """
    from bigchaindb.models import Transaction
    from bigchaindb.common.exceptions import DoubleSpend

    # create a divisible asset
    tx_create = Transaction.create([b.me], [([b.me], 100)])
    tx_create_signed = tx_create.sign([b.me_private])
    assert b.validate_transaction(tx_create_signed) == tx_create_signed

    # create a block and valid vote
    block = b.create_block([tx_create_signed])
    b.write_block(block)
    vote = b.vote(block.id, genesis_block.id, True)
    b.write_vote(vote)

    # Create a transfer transaction with duplicated fulfillments
    dup_inputs = tx_create.to_inputs() + tx_create.to_inputs()
    tx_transfer = Transaction.transfer(dup_inputs, [([b.me], 200)],
                                       asset_id=tx_create.id)
    tx_transfer_signed = tx_transfer.sign([b.me_private])
    with pytest.raises(DoubleSpend):
        tx_transfer_signed.validate(b)


@pytest.mark.bdb
def test_transaction_unicode(b):
    from bigchaindb.common.utils import serialize
    from bigchaindb.models import Transaction

    # http://www.fileformat.info/info/unicode/char/1f37a/index.htm
    beer_python = {'beer': '\N{BEER MUG}'}
    beer_json = '{"beer":"\N{BEER MUG}"}'

    tx = (Transaction.create([b.me], [([b.me], 100)], beer_python)
          ).sign([b.me_private])
    block = b.create_block([tx])
    b.write_block(block)
    assert b.get_block(block.id) == block.to_dict()
    assert block.validate(b) == block
    assert beer_json in serialize(block.to_dict())


@pytest.mark.bdb
def test_is_new_transaction(b, genesis_block):
    from bigchaindb.models import Transaction

    def write_tx(n):
        tx = Transaction.create([b.me], [([b.me], n)])
        tx = tx.sign([b.me_private])
        # Tx is new because it's not in any block
        assert b.is_new_transaction(tx.id)

        block = b.create_block([tx])
        b.write_block(block)
        return tx, block

    # test VALID case
    tx, block = write_tx(1)
    # Tx is now in undecided block
    assert not b.is_new_transaction(tx.id)
    assert b.is_new_transaction(tx.id, exclude_block_id=block.id)
    # After voting valid, should not be new
    vote = b.vote(block.id, genesis_block.id, True)
    b.write_vote(vote)
    assert not b.is_new_transaction(tx.id)
    assert b.is_new_transaction(tx.id, exclude_block_id=block.id)

    # test INVALID case
    tx, block = write_tx(2)
    # Tx is now in undecided block
    assert not b.is_new_transaction(tx.id)
    assert b.is_new_transaction(tx.id, exclude_block_id=block.id)
    vote = b.vote(block.id, genesis_block.id, False)
    b.write_vote(vote)
    # Tx is new because it's only found in an invalid block
    assert b.is_new_transaction(tx.id)
    assert b.is_new_transaction(tx.id, exclude_block_id=block.id)
