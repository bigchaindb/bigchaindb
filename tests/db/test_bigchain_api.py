# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

from unittest.mock import patch

import pytest
from base58 import b58decode

pytestmark = pytest.mark.bdb


class TestBigchainApi(object):

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

    def test_double_inclusion(self, b, alice):
        from bigchaindb.models import Transaction
        from bigchaindb.backend.exceptions import OperationError

        tx = Transaction.create([alice.public_key], [([alice.public_key], 1)])
        tx = tx.sign([alice.private_key])

        b.store_bulk_transactions([tx])

        with pytest.raises(OperationError):
            b.store_bulk_transactions([tx])

    def test_text_search(self, b, alice):
        from bigchaindb.models import Transaction

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
        assets = list(b.text_search('bigchaindb'))
        assert len(assets) == 3

    @pytest.mark.usefixtures('inputs')
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

    def test_non_create_input_not_found(self, b, signed_transfer_tx):
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

        input_tx = b.fastquery.get_outputs_by_public_key(user_pk).pop()
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

        b.store_bulk_transactions([signed_create_tx, signed_transfer_tx])

        with pytest.raises(DoubleSpend):
            b.validate_transaction(double_spend_tx)


class TestMultipleInputs(object):

    def test_transfer_single_owner_single_input(self, b, inputs, user_pk,
                                                user_sk):
        from bigchaindb.common import crypto
        from bigchaindb.models import Transaction

        user2_sk, user2_pk = crypto.generate_key_pair()

        tx_link = b.fastquery.get_outputs_by_public_key(user_pk).pop()
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
        tx_link = b.fastquery.get_outputs_by_public_key(user_pk).pop()

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
        b.store_bulk_transactions([tx])

        owned_input = b.fastquery.get_outputs_by_public_key(user_pk).pop()
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
        b.store_bulk_transactions([tx])

        # get input
        tx_link = b.fastquery.get_outputs_by_public_key(user_pk).pop()
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
        b.store_bulk_transactions([tx])

        owned_inputs_user1 = b.fastquery.get_outputs_by_public_key(user_pk)
        owned_inputs_user2 = b.fastquery.get_outputs_by_public_key(user2_pk)
        assert owned_inputs_user1 == [TransactionLink(tx.id, 0)]
        assert owned_inputs_user2 == []

        tx_transfer = Transaction.transfer(tx.to_inputs(), [([user2_pk], 1)],
                                           asset_id=tx.id)
        tx_transfer = tx_transfer.sign([user_sk])
        b.store_bulk_transactions([tx_transfer])

        owned_inputs_user1 = b.fastquery.get_outputs_by_public_key(user_pk)
        owned_inputs_user2 = b.fastquery.get_outputs_by_public_key(user2_pk)

        assert owned_inputs_user1 == [TransactionLink(tx.id, 0)]
        assert owned_inputs_user2 == [TransactionLink(tx_transfer.id, 0)]

    def test_get_owned_ids_single_tx_multiple_outputs(self, b, user_sk,
                                                      user_pk, alice):
        from bigchaindb.common import crypto
        from bigchaindb.common.transaction import TransactionLink
        from bigchaindb.models import Transaction

        user2_sk, user2_pk = crypto.generate_key_pair()

        # create divisible asset
        tx_create = Transaction.create([alice.public_key], [([user_pk], 1), ([user_pk], 1)])
        tx_create_signed = tx_create.sign([alice.private_key])
        b.store_bulk_transactions([tx_create_signed])

        # get input
        owned_inputs_user1 = b.fastquery.get_outputs_by_public_key(user_pk)
        owned_inputs_user2 = b.fastquery.get_outputs_by_public_key(user2_pk)

        expected_owned_inputs_user1 = [TransactionLink(tx_create.id, 0),
                                       TransactionLink(tx_create.id, 1)]
        assert owned_inputs_user1 == expected_owned_inputs_user1
        assert owned_inputs_user2 == []

        # transfer divisible asset divided in two outputs
        tx_transfer = Transaction.transfer(tx_create.to_inputs(),
                                           [([user2_pk], 1), ([user2_pk], 1)],
                                           asset_id=tx_create.id)
        tx_transfer_signed = tx_transfer.sign([user_sk])
        b.store_bulk_transactions([tx_transfer_signed])

        owned_inputs_user1 = b.fastquery.get_outputs_by_public_key(user_pk)
        owned_inputs_user2 = b.fastquery.get_outputs_by_public_key(user2_pk)
        assert owned_inputs_user1 == expected_owned_inputs_user1
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

        b.store_bulk_transactions([tx])

        owned_inputs_user1 = b.fastquery.get_outputs_by_public_key(user_pk)
        owned_inputs_user2 = b.fastquery.get_outputs_by_public_key(user_pk)
        expected_owned_inputs_user1 = [TransactionLink(tx.id, 0)]

        assert owned_inputs_user1 == owned_inputs_user2
        assert owned_inputs_user1 == expected_owned_inputs_user1

        tx = Transaction.transfer(tx.to_inputs(), [([user3_pk], 1)],
                                  asset_id=tx.id)
        tx = tx.sign([user_sk, user2_sk])
        b.store_bulk_transactions([tx])

        owned_inputs_user1 = b.fastquery.get_outputs_by_public_key(user_pk)
        owned_inputs_user2 = b.fastquery.get_outputs_by_public_key(user2_pk)
        spent_user1 = b.get_spent(tx.id, 0)

        assert owned_inputs_user1 == owned_inputs_user2
        assert not spent_user1

    def test_get_spent_single_tx_single_output(self, b, user_sk, user_pk, alice):
        from bigchaindb.common import crypto
        from bigchaindb.models import Transaction

        user2_sk, user2_pk = crypto.generate_key_pair()

        tx = Transaction.create([alice.public_key], [([user_pk], 1)])
        tx = tx.sign([alice.private_key])
        b.store_bulk_transactions([tx])

        owned_inputs_user1 = b.fastquery.get_outputs_by_public_key(user_pk).pop()

        # check spents
        input_txid = owned_inputs_user1.txid
        spent_inputs_user1 = b.get_spent(input_txid, 0)
        assert spent_inputs_user1 is None

        # create a transaction and send it
        tx = Transaction.transfer(tx.to_inputs(), [([user2_pk], 1)],
                                  asset_id=tx.id)
        tx = tx.sign([user_sk])
        b.store_bulk_transactions([tx])

        spent_inputs_user1 = b.get_spent(input_txid, 0)
        assert spent_inputs_user1 == tx

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
        b.store_bulk_transactions([tx_create_signed])

        owned_inputs_user1 = b.fastquery.get_outputs_by_public_key(user_pk)

        # check spents
        for input_tx in owned_inputs_user1:
            assert b.get_spent(input_tx.txid, input_tx.output) is None

        # transfer the first 2 inputs
        tx_transfer = Transaction.transfer(tx_create.to_inputs()[:2],
                                           [([user2_pk], 1), ([user2_pk], 1)],
                                           asset_id=tx_create.id)
        tx_transfer_signed = tx_transfer.sign([user_sk])
        b.store_bulk_transactions([tx_transfer_signed])

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

        b.store_bulk_transactions(transactions)

        owned_inputs_user1 = b.fastquery.get_outputs_by_public_key(user_pk)
        # check spents
        for input_tx in owned_inputs_user1:
            assert b.get_spent(input_tx.txid, input_tx.output) is None

        # create a transaction
        tx = Transaction.transfer(transactions[0].to_inputs(),
                                  [([user3_pk], 1)],
                                  asset_id=transactions[0].id)
        tx = tx.sign([user_sk, user2_sk])
        b.store_bulk_transactions([tx])

        # check that used inputs are marked as spent
        assert b.get_spent(transactions[0].id, 0) == tx
        # check that the other remain marked as unspent
        for unspent in transactions[1:]:
            assert b.get_spent(unspent.id, 0) is None


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


def test_cant_spend_same_input_twice_in_tx(b, alice):
    """Recreate duplicated fulfillments bug
    https://github.com/bigchaindb/bigchaindb/issues/1099
    """
    from bigchaindb.models import Transaction
    from bigchaindb.common.exceptions import DoubleSpend

    # create a divisible asset
    tx_create = Transaction.create([alice.public_key], [([alice.public_key], 100)])
    tx_create_signed = tx_create.sign([alice.private_key])
    assert b.validate_transaction(tx_create_signed) == tx_create_signed

    b.store_bulk_transactions([tx_create_signed])

    # Create a transfer transaction with duplicated fulfillments
    dup_inputs = tx_create.to_inputs() + tx_create.to_inputs()
    tx_transfer = Transaction.transfer(dup_inputs, [([alice.public_key], 200)],
                                       asset_id=tx_create.id)
    tx_transfer_signed = tx_transfer.sign([alice.private_key])
    with pytest.raises(DoubleSpend):
        tx_transfer_signed.validate(b)


def test_transaction_unicode(b, alice):
    import copy
    from bigchaindb.common.utils import serialize
    from bigchaindb.models import Transaction

    # http://www.fileformat.info/info/unicode/char/1f37a/index.htm
    beer_python = {'beer': '\N{BEER MUG}'}
    beer_json = '{"beer":"\N{BEER MUG}"}'

    tx = (Transaction.create([alice.public_key], [([alice.public_key], 100)], beer_python)
          ).sign([alice.private_key])

    tx_1 = copy.deepcopy(tx)
    b.store_bulk_transactions([tx])

    assert beer_json in serialize(tx_1.to_dict())
