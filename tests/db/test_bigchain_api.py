# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

from time import sleep
from unittest.mock import patch

import pytest
from base58 import b58decode

pytestmark = pytest.mark.bdb


class TestBigchainApi(object):

    @pytest.mark.tendermint
    def test_get_spent_with_double_inclusion_detected(self, b, alice):
        from bigchaindb.models import Transaction
        from bigchaindb.backend.exceptions import OperationError

        tx = Transaction.create([alice.public_key], [([alice.public_key], 1)])
        tx = tx.sign([alice.private_key])

        b.store_bulk_transactions([tx])

        transfer_tx = Transaction.transfer(tx.to_inputs(), [([alice.public_key], 1)],
                                           asset_id=tx.id)
        transfer_tx = transfer_tx.sign([alice.private_key])
        b.store_bulk_transactions([transfer_tx])

        transfer_tx2 = Transaction.transfer(tx.to_inputs(), [([alice.public_key], 1)],
                                            asset_id=tx.id)
        transfer_tx2 = transfer_tx2.sign([alice.private_key])
        with pytest.raises(OperationError):
            b.store_bulk_transactions([transfer_tx2])

    @pytest.mark.tendermint
    def test_get_spent_with_double_spend_detected(self, b, alice):
        from bigchaindb.models import Transaction
        from bigchaindb.common.exceptions import DoubleSpend
        from bigchaindb.exceptions import CriticalDoubleSpend

        tx = Transaction.create([alice.public_key], [([alice.public_key], 1)])
        tx = tx.sign([alice.private_key])

        b.store_bulk_transactions([tx])

        transfer_tx = Transaction.transfer(tx.to_inputs(), [([alice.public_key], 1)],
                                           asset_id=tx.id)
        transfer_tx = transfer_tx.sign([alice.private_key])
        transfer_tx2 = Transaction.transfer(tx.to_inputs(), [([alice.public_key], 2)],
                                            asset_id=tx.id)
        transfer_tx2 = transfer_tx2.sign([alice.private_key])

        with pytest.raises(DoubleSpend):
            b.validate_transaction(transfer_tx2, [transfer_tx])

        b.store_bulk_transactions([transfer_tx])

        with pytest.raises(DoubleSpend):
            b.validate_transaction(transfer_tx2)

        b.store_bulk_transactions([transfer_tx2])

        with pytest.raises(CriticalDoubleSpend):
            b.get_spent(tx.id, 0)

    @pytest.mark.tendermint
    def test_get_block_status_for_tx_with_double_inclusion(self, b, alice):
        from bigchaindb.models import Transaction
        from bigchaindb.backend.exceptions import OperationError

        tx = Transaction.create([alice.public_key], [([alice.public_key], 1)])
        tx = tx.sign([alice.private_key])

        b.store_bulk_transactions([tx])

        with pytest.raises(OperationError):
            b.store_bulk_transactions([tx])

    @pytest.mark.tendermint
    def test_text_search(self, b, alice):
        from bigchaindb.models import Transaction
        from bigchaindb.backend.exceptions import OperationError
        from bigchaindb.backend.localmongodb.connection import LocalMongoDBConnection

        # define the assets
        asset1 = {'msg': 'BigchainDB 1'}
        asset2 = {'msg': 'BigchainDB 2'}
        asset3 = {'msg': 'BigchainDB 3'}

        # create the transactions
        tx1 = Transaction.create([alice.public_key], [([alice.public_key], 1)],
                                 asset=asset1).sign([alice.private_key])
        tx2 = Transaction.create([alice.public_key], [([alice.public_key], 1)],
                                 asset=asset2).sign([alice.private_key])
        tx3 = Transaction.create([alice.public_key], [([alice.public_key], 1)],
                                 asset=asset3).sign([alice.private_key])

        # write the transactions to the DB
        b.store_bulk_transactions([tx1, tx2, tx3])

        # get the assets through text search
        # this query only works with MongoDB
        try:
            assets = list(b.text_search('bigchaindb'))
        except OperationError as exc:
            assert not isinstance(b.connection, LocalMongoDBConnection)
        else:
            assert len(assets) == 3

    @pytest.mark.usefixtures('inputs')
    @pytest.mark.tendermint
    def test_non_create_input_not_found(self, b, user_pk):
        from cryptoconditions import Ed25519Sha256
        from bigchaindb.common.exceptions import InputDoesNotExist
        from bigchaindb.common.transaction import Input, TransactionLink
        from bigchaindb.models import Transaction

        # Create an input for a non existing transaction
        input = Input(Ed25519Sha256(public_key=b58decode(user_pk)),
                      [user_pk],
                      TransactionLink('somethingsomething', 0))
        tx = Transaction.transfer([input], [([user_pk], 1)],
                                  asset_id='mock_asset_link')
        with pytest.raises(InputDoesNotExist):
            tx.validate(b)

    @pytest.mark.tendermint
    def test_write_transaction(self, b, user_sk, user_pk, alice, create_tx):
        from bigchaindb.models import Transaction

        asset1 = {'msg': 'BigchainDB 1'}

        tx = Transaction.create([alice.public_key], [([alice.public_key], 1)],
                                asset=asset1).sign([alice.private_key])
        b.store_bulk_transactions([tx])

        tx_from_db = b.get_transaction(tx.id)

        before = tx.to_dict()
        after = tx_from_db.to_dict()

        assert before['asset']['data'] == after['asset']['data']
        before.pop('asset', None)
        after.pop('asset', None)
        assert before == after


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
                                                                    user_pk,
                                                                    alice):
        from bigchaindb.common import crypto
        from bigchaindb.models import Transaction

        user2_sk, user2_pk = crypto.generate_key_pair()
        user3_sk, user3_pk = crypto.generate_key_pair()

        tx = Transaction.create([alice.public_key], [([user_pk, user2_pk], 1)])
        tx = tx.sign([alice.private_key])
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
                                                                       user_pk,
                                                                       alice):
        from bigchaindb.common import crypto
        from bigchaindb.models import Transaction

        user2_sk, user2_pk = crypto.generate_key_pair()
        user3_sk, user3_pk = crypto.generate_key_pair()
        user4_sk, user4_pk = crypto.generate_key_pair()

        tx = Transaction.create([alice.public_key], [([user_pk, user2_pk], 1)])
        tx = tx.sign([alice.private_key])
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

    def test_get_owned_ids_single_tx_single_output(self, b, user_sk, user_pk, alice):
        from bigchaindb.common import crypto
        from bigchaindb.common.transaction import TransactionLink
        from bigchaindb.models import Transaction

        user2_sk, user2_pk = crypto.generate_key_pair()

        tx = Transaction.create([alice.public_key], [([user_pk], 1)])
        tx = tx.sign([alice.private_key])
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
                                                                 genesis_block,
                                                                 alice):
        from bigchaindb.common import crypto
        from bigchaindb.common.transaction import TransactionLink
        from bigchaindb.models import Transaction

        user2_sk, user2_pk = crypto.generate_key_pair()

        tx = Transaction.create([alice.public_key], [([user_pk], 1)])
        tx = tx.sign([alice.private_key])
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
                                                      user_pk, alice):
        from bigchaindb.common import crypto
        from bigchaindb.common.transaction import TransactionLink
        from bigchaindb.models import Transaction

        user2_sk, user2_pk = crypto.generate_key_pair()

        # create divisible asset
        tx_create = Transaction.create([alice.public_key], [([user_pk], 1), ([user_pk], 1)])
        tx_create_signed = tx_create.sign([alice.private_key])
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

    def test_get_owned_ids_multiple_owners(self, b, user_sk, user_pk, alice):
        from bigchaindb.common import crypto
        from bigchaindb.common.transaction import TransactionLink
        from bigchaindb.models import Transaction

        user2_sk, user2_pk = crypto.generate_key_pair()
        user3_sk, user3_pk = crypto.generate_key_pair()

        tx = Transaction.create([alice.public_key], [([user_pk, user2_pk], 1)])
        tx = tx.sign([alice.private_key])
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

    def test_get_spent_single_tx_single_output(self, b, user_sk, user_pk, alice):
        from bigchaindb.common import crypto
        from bigchaindb.models import Transaction

        user2_sk, user2_pk = crypto.generate_key_pair()

        tx = Transaction.create([alice.public_key], [([user_pk], 1)])
        tx = tx.sign([alice.private_key])
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
                                                             genesis_block,
                                                             alice):
        from bigchaindb.common import crypto
        from bigchaindb.models import Transaction

        # create a new users
        user2_sk, user2_pk = crypto.generate_key_pair()

        tx = Transaction.create([alice.public_key], [([user_pk], 1)])
        tx = tx.sign([alice.private_key])
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

    def test_get_spent_single_tx_multiple_outputs(self, b, user_sk, user_pk, alice):
        from bigchaindb.common import crypto
        from bigchaindb.models import Transaction

        # create a new users
        user2_sk, user2_pk = crypto.generate_key_pair()

        # create a divisible asset with 3 outputs
        tx_create = Transaction.create([alice.public_key],
                                       [([user_pk], 1),
                                        ([user_pk], 1),
                                        ([user_pk], 1)])
        tx_create_signed = tx_create.sign([alice.private_key])
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

    def test_get_spent_multiple_owners(self, b, user_sk, user_pk, alice):
        from bigchaindb.common import crypto
        from bigchaindb.models import Transaction

        user2_sk, user2_pk = crypto.generate_key_pair()
        user3_sk, user3_pk = crypto.generate_key_pair()

        transactions = []
        for i in range(3):
            payload = {'somedata': i}
            tx = Transaction.create([alice.public_key], [([user_pk, user2_pk], 1)],
                                    payload)
            tx = tx.sign([alice.private_key])
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
    from bigchaindb import BigchainDB
    with patch('bigchaindb.BigchainDB.get_outputs_filtered') as gof:
        b = BigchainDB()
        res = b.get_owned_ids('abc')
    gof.assert_called_once_with('abc', spent=False)
    assert res == gof()


@pytest.mark.tendermint
def test_get_outputs_filtered_only_unspent():
    from bigchaindb.common.transaction import TransactionLink
    from bigchaindb.lib import BigchainDB

    go = 'bigchaindb.fastquery.FastQuery.get_outputs_by_public_key'
    with patch(go) as get_outputs:
        get_outputs.return_value = [TransactionLink('a', 1),
                                    TransactionLink('b', 2)]
        fs = 'bigchaindb.fastquery.FastQuery.filter_spent_outputs'
        with patch(fs) as filter_spent:
            filter_spent.return_value = [TransactionLink('b', 2)]
            out = BigchainDB().get_outputs_filtered('abc', spent=False)
    get_outputs.assert_called_once_with('abc')
    assert out == [TransactionLink('b', 2)]


@pytest.mark.tendermint
def test_get_outputs_filtered_only_spent():
    from bigchaindb.common.transaction import TransactionLink
    from bigchaindb.lib import BigchainDB
    go = 'bigchaindb.fastquery.FastQuery.get_outputs_by_public_key'
    with patch(go) as get_outputs:
        get_outputs.return_value = [TransactionLink('a', 1),
                                    TransactionLink('b', 2)]
        fs = 'bigchaindb.fastquery.FastQuery.filter_unspent_outputs'
        with patch(fs) as filter_spent:
            filter_spent.return_value = [TransactionLink('b', 2)]
            out = BigchainDB().get_outputs_filtered('abc', spent=True)
    get_outputs.assert_called_once_with('abc')
    assert out == [TransactionLink('b', 2)]


@pytest.mark.tendermint
@patch('bigchaindb.fastquery.FastQuery.filter_unspent_outputs')
@patch('bigchaindb.fastquery.FastQuery.filter_spent_outputs')
def test_get_outputs_filtered(filter_spent, filter_unspent):
    from bigchaindb.common.transaction import TransactionLink
    from bigchaindb.lib import BigchainDB

    go = 'bigchaindb.fastquery.FastQuery.get_outputs_by_public_key'
    with patch(go) as get_outputs:
        get_outputs.return_value = [TransactionLink('a', 1),
                                    TransactionLink('b', 2)]
        out = BigchainDB().get_outputs_filtered('abc')
    get_outputs.assert_called_once_with('abc')
    filter_spent.assert_not_called()
    filter_unspent.assert_not_called()
    assert out == get_outputs.return_value


@pytest.mark.bdb
def test_cant_spend_same_input_twice_in_tx(b, genesis_block, alice):
    """Recreate duplicated fulfillments bug
    https://github.com/bigchaindb/bigchaindb/issues/1099
    """
    from bigchaindb.models import Transaction
    from bigchaindb.common.exceptions import DoubleSpend

    # create a divisible asset
    tx_create = Transaction.create([alice.public_key], [([alice.public_key], 100)])
    tx_create_signed = tx_create.sign([alice.private_key])
    assert b.validate_transaction(tx_create_signed) == tx_create_signed

    # create a block and valid vote
    block = b.create_block([tx_create_signed])
    b.write_block(block)
    vote = b.vote(block.id, genesis_block.id, True)
    b.write_vote(vote)

    # Create a transfer transaction with duplicated fulfillments
    dup_inputs = tx_create.to_inputs() + tx_create.to_inputs()
    tx_transfer = Transaction.transfer(dup_inputs, [([alice.public_key], 200)],
                                       asset_id=tx_create.id)
    tx_transfer_signed = tx_transfer.sign([alice.private_key])
    with pytest.raises(DoubleSpend):
        tx_transfer_signed.validate(b)


@pytest.mark.bdb
def test_transaction_unicode(b, alice):
    from bigchaindb.common.utils import serialize
    from bigchaindb.models import Transaction

    # http://www.fileformat.info/info/unicode/char/1f37a/index.htm
    beer_python = {'beer': '\N{BEER MUG}'}
    beer_json = '{"beer":"\N{BEER MUG}"}'

    tx = (Transaction.create([alice.public_key], [([alice.public_key], 100)], beer_python)
          ).sign([alice.private_key])
    block = b.create_block([tx])
    b.write_block(block)
    assert b.get_block(block.id) == block.to_dict()
    assert block.validate(b) == block
    assert beer_json in serialize(block.to_dict())


@pytest.mark.bdb
def test_is_new_transaction(b, genesis_block, alice):
    from bigchaindb.models import Transaction

    def write_tx(n):
        tx = Transaction.create([alice.public_key], [([alice.public_key], n)])
        tx = tx.sign([alice.private_key])
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
