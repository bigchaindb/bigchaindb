# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

import pytest
import random

from bigchaindb.common.exceptions import DoubleSpend


# CREATE divisible asset
# Single input
# Single owners_before
# Single output
# Single owners_after
def test_single_in_single_own_single_out_single_own_create(alice, user_pk, b):
    from bigchaindb.models import Transaction

    tx = Transaction.create([alice.public_key], [([user_pk], 100)], asset={'name': random.random()})
    tx_signed = tx.sign([alice.private_key])

    assert tx_signed.validate(b) == tx_signed
    assert len(tx_signed.outputs) == 1
    assert tx_signed.outputs[0].amount == 100
    assert len(tx_signed.inputs) == 1


# CREATE divisible asset
# Single input
# Single owners_before
# Multiple outputs
# Single owners_after per output
def test_single_in_single_own_multiple_out_single_own_create(alice, user_pk, b):
    from bigchaindb.models import Transaction

    tx = Transaction.create([alice.public_key], [([user_pk], 50), ([user_pk], 50)],
                            asset={'name': random.random()})
    tx_signed = tx.sign([alice.private_key])

    assert tx_signed.validate(b) == tx_signed
    assert len(tx_signed.outputs) == 2
    assert tx_signed.outputs[0].amount == 50
    assert tx_signed.outputs[1].amount == 50
    assert len(tx_signed.inputs) == 1


# CREATE divisible asset
# Single input
# Single owners_before
# Single output
# Multiple owners_after
def test_single_in_single_own_single_out_multiple_own_create(alice, user_pk, b):
    from bigchaindb.models import Transaction

    tx = Transaction.create([alice.public_key], [([user_pk, user_pk], 100)], asset={'name': random.random()})
    tx_signed = tx.sign([alice.private_key])

    assert tx_signed.validate(b) == tx_signed
    assert len(tx_signed.outputs) == 1
    assert tx_signed.outputs[0].amount == 100

    output = tx_signed.outputs[0].to_dict()
    assert 'subconditions' in output['condition']['details']
    assert len(output['condition']['details']['subconditions']) == 2

    assert len(tx_signed.inputs) == 1


# CREATE divisible asset
# Single input
# Single owners_before
# Multiple outputs
# Mix: one output with a single owners_after, one output with multiple
#      owners_after
def test_single_in_single_own_multiple_out_mix_own_create(alice, user_pk, b):
    from bigchaindb.models import Transaction

    tx = Transaction.create([alice.public_key], [([user_pk], 50), ([user_pk, user_pk], 50)],
                            asset={'name': random.random()})
    tx_signed = tx.sign([alice.private_key])

    assert tx_signed.validate(b) == tx_signed
    assert len(tx_signed.outputs) == 2
    assert tx_signed.outputs[0].amount == 50
    assert tx_signed.outputs[1].amount == 50

    output_cid1 = tx_signed.outputs[1].to_dict()
    assert 'subconditions' in output_cid1['condition']['details']
    assert len(output_cid1['condition']['details']['subconditions']) == 2

    assert len(tx_signed.inputs) == 1


# CREATE divisible asset
# Single input
# Multiple owners_before
# Output combinations already tested above
def test_single_in_multiple_own_single_out_single_own_create(alice, b, user_pk,
                                                             user_sk):
    from bigchaindb.models import Transaction
    from bigchaindb.common.transaction import _fulfillment_to_details

    tx = Transaction.create([alice.public_key, user_pk], [([user_pk], 100)], asset={'name': random.random()})
    tx_signed = tx.sign([alice.private_key, user_sk])
    assert tx_signed.validate(b) == tx_signed
    assert len(tx_signed.outputs) == 1
    assert tx_signed.outputs[0].amount == 100
    assert len(tx_signed.inputs) == 1

    ffill = _fulfillment_to_details(tx_signed.inputs[0].fulfillment)
    assert 'subconditions' in ffill
    assert len(ffill['subconditions']) == 2


# TRANSFER divisible asset
# Single input
# Single owners_before
# Single output
# Single owners_after
def test_single_in_single_own_single_out_single_own_transfer(alice, b, user_pk,
                                                             user_sk):
    from bigchaindb.models import Transaction

    # CREATE divisible asset
    tx_create = Transaction.create([alice.public_key], [([user_pk], 100)], asset={'name': random.random()})
    tx_create_signed = tx_create.sign([alice.private_key])

    # TRANSFER
    tx_transfer = Transaction.transfer(tx_create.to_inputs(), [([alice.public_key], 100)],
                                       asset_id=tx_create.id)
    tx_transfer_signed = tx_transfer.sign([user_sk])

    b.store_bulk_transactions([tx_create_signed])

    assert tx_transfer_signed.validate(b)
    assert len(tx_transfer_signed.outputs) == 1
    assert tx_transfer_signed.outputs[0].amount == 100
    assert len(tx_transfer_signed.inputs) == 1


# TRANSFER divisible asset
# Single input
# Single owners_before
# Multiple output
# Single owners_after
def test_single_in_single_own_multiple_out_single_own_transfer(alice, b, user_pk,
                                                               user_sk):
    from bigchaindb.models import Transaction

    # CREATE divisible asset
    tx_create = Transaction.create([alice.public_key], [([user_pk], 100)], asset={'name': random.random()})
    tx_create_signed = tx_create.sign([alice.private_key])

    # TRANSFER
    tx_transfer = Transaction.transfer(tx_create.to_inputs(),
                                       [([alice.public_key], 50), ([alice.public_key], 50)],
                                       asset_id=tx_create.id)
    tx_transfer_signed = tx_transfer.sign([user_sk])

    b.store_bulk_transactions([tx_create_signed])

    assert tx_transfer_signed.validate(b) == tx_transfer_signed
    assert len(tx_transfer_signed.outputs) == 2
    assert tx_transfer_signed.outputs[0].amount == 50
    assert tx_transfer_signed.outputs[1].amount == 50
    assert len(tx_transfer_signed.inputs) == 1


# TRANSFER divisible asset
# Single input
# Single owners_before
# Single output
# Multiple owners_after
def test_single_in_single_own_single_out_multiple_own_transfer(alice, b, user_pk,
                                                               user_sk):
    from bigchaindb.models import Transaction

    # CREATE divisible asset
    tx_create = Transaction.create([alice.public_key], [([user_pk], 100)], asset={'name': random.random()})
    tx_create_signed = tx_create.sign([alice.private_key])

    # TRANSFER
    tx_transfer = Transaction.transfer(tx_create.to_inputs(),
                                       [([alice.public_key, alice.public_key], 100)],
                                       asset_id=tx_create.id)
    tx_transfer_signed = tx_transfer.sign([user_sk])

    b.store_bulk_transactions([tx_create_signed])

    assert tx_transfer_signed.validate(b) == tx_transfer_signed
    assert len(tx_transfer_signed.outputs) == 1
    assert tx_transfer_signed.outputs[0].amount == 100

    condition = tx_transfer_signed.outputs[0].to_dict()
    assert 'subconditions' in condition['condition']['details']
    assert len(condition['condition']['details']['subconditions']) == 2

    assert len(tx_transfer_signed.inputs) == 1

    b.store_bulk_transactions([tx_transfer_signed])
    with pytest.raises(DoubleSpend):
        tx_transfer_signed.validate(b)


# TRANSFER divisible asset
# Single input
# Single owners_before
# Multiple outputs
# Mix: one output with a single owners_after, one output with multiple
#      owners_after
def test_single_in_single_own_multiple_out_mix_own_transfer(alice, b, user_pk,
                                                            user_sk):
    from bigchaindb.models import Transaction

    # CREATE divisible asset
    tx_create = Transaction.create([alice.public_key], [([user_pk], 100)], asset={'name': random.random()})
    tx_create_signed = tx_create.sign([alice.private_key])

    # TRANSFER
    tx_transfer = Transaction.transfer(tx_create.to_inputs(),
                                       [([alice.public_key], 50), ([alice.public_key, alice.public_key], 50)],
                                       asset_id=tx_create.id)
    tx_transfer_signed = tx_transfer.sign([user_sk])

    b.store_bulk_transactions([tx_create_signed])

    assert tx_transfer_signed.validate(b) == tx_transfer_signed
    assert len(tx_transfer_signed.outputs) == 2
    assert tx_transfer_signed.outputs[0].amount == 50
    assert tx_transfer_signed.outputs[1].amount == 50

    output_cid1 = tx_transfer_signed.outputs[1].to_dict()
    assert 'subconditions' in output_cid1['condition']['details']
    assert len(output_cid1['condition']['details']['subconditions']) == 2

    assert len(tx_transfer_signed.inputs) == 1

    b.store_bulk_transactions([tx_transfer_signed])
    with pytest.raises(DoubleSpend):
        tx_transfer_signed.validate(b)


# TRANSFER divisible asset
# Single input
# Multiple owners_before
# Single output
# Single owners_after
def test_single_in_multiple_own_single_out_single_own_transfer(alice, b, user_pk,
                                                               user_sk):
    from bigchaindb.models import Transaction
    from bigchaindb.common.transaction import _fulfillment_to_details

    # CREATE divisible asset
    tx_create = Transaction.create([alice.public_key], [([alice.public_key, user_pk], 100)],
                                   asset={'name': random.random()})
    tx_create_signed = tx_create.sign([alice.private_key])

    # TRANSFER
    tx_transfer = Transaction.transfer(tx_create.to_inputs(), [([alice.public_key], 100)],
                                       asset_id=tx_create.id)
    tx_transfer_signed = tx_transfer.sign([alice.private_key, user_sk])

    b.store_bulk_transactions([tx_create_signed])

    assert tx_transfer_signed.validate(b) == tx_transfer_signed
    assert len(tx_transfer_signed.outputs) == 1
    assert tx_transfer_signed.outputs[0].amount == 100
    assert len(tx_transfer_signed.inputs) == 1

    ffill = _fulfillment_to_details(tx_transfer_signed.inputs[0].fulfillment)
    assert 'subconditions' in ffill
    assert len(ffill['subconditions']) == 2

    b.store_bulk_transactions([tx_transfer_signed])
    with pytest.raises(DoubleSpend):
        tx_transfer_signed.validate(b)


# TRANSFER divisible asset
# Multiple inputs
# Single owners_before per input
# Single output
# Single owners_after
def test_multiple_in_single_own_single_out_single_own_transfer(alice, b, user_pk,
                                                               user_sk):
    from bigchaindb.models import Transaction

    # CREATE divisible asset
    tx_create = Transaction.create([alice.public_key], [([user_pk], 50), ([user_pk], 50)],
                                   asset={'name': random.random()})
    tx_create_signed = tx_create.sign([alice.private_key])

    # TRANSFER
    tx_transfer = Transaction.transfer(tx_create.to_inputs(), [([alice.public_key], 100)],
                                       asset_id=tx_create.id)
    tx_transfer_signed = tx_transfer.sign([user_sk])

    b.store_bulk_transactions([tx_create_signed])

    assert tx_transfer_signed.validate(b)
    assert len(tx_transfer_signed.outputs) == 1
    assert tx_transfer_signed.outputs[0].amount == 100
    assert len(tx_transfer_signed.inputs) == 2

    b.store_bulk_transactions([tx_transfer_signed])
    with pytest.raises(DoubleSpend):
        tx_transfer_signed.validate(b)


# TRANSFER divisible asset
# Multiple inputs
# Multiple owners_before per input
# Single output
# Single owners_after
def test_multiple_in_multiple_own_single_out_single_own_transfer(alice, b, user_pk,
                                                                 user_sk):
    from bigchaindb.models import Transaction
    from bigchaindb.common.transaction import _fulfillment_to_details

    # CREATE divisible asset
    tx_create = Transaction.create([alice.public_key], [([user_pk, alice.public_key], 50),
                                   ([user_pk, alice.public_key], 50)],
                                   asset={'name': random.random()})
    tx_create_signed = tx_create.sign([alice.private_key])

    # TRANSFER
    tx_transfer = Transaction.transfer(tx_create.to_inputs(), [([alice.public_key], 100)],
                                       asset_id=tx_create.id)
    tx_transfer_signed = tx_transfer.sign([alice.private_key, user_sk])

    b.store_bulk_transactions([tx_create_signed])

    assert tx_transfer_signed.validate(b) == tx_transfer_signed
    assert len(tx_transfer_signed.outputs) == 1
    assert tx_transfer_signed.outputs[0].amount == 100
    assert len(tx_transfer_signed.inputs) == 2

    ffill_fid0 = _fulfillment_to_details(tx_transfer_signed.inputs[0].fulfillment)
    ffill_fid1 = _fulfillment_to_details(tx_transfer_signed.inputs[1].fulfillment)
    assert 'subconditions' in ffill_fid0
    assert 'subconditions' in ffill_fid1
    assert len(ffill_fid0['subconditions']) == 2
    assert len(ffill_fid1['subconditions']) == 2

    b.store_bulk_transactions([tx_transfer_signed])
    with pytest.raises(DoubleSpend):
        tx_transfer_signed.validate(b)


# TRANSFER divisible asset
# Multiple inputs
# Mix: one input with a single owners_before, one input with multiple
#      owners_before
# Single output
# Single owners_after
def test_muiltiple_in_mix_own_multiple_out_single_own_transfer(alice, b, user_pk,
                                                               user_sk):
    from bigchaindb.models import Transaction
    from bigchaindb.common.transaction import _fulfillment_to_details

    # CREATE divisible asset
    tx_create = Transaction.create([alice.public_key], [([user_pk], 50), ([user_pk, alice.public_key], 50)],
                                   asset={'name': random.random()})
    tx_create_signed = tx_create.sign([alice.private_key])

    # TRANSFER
    tx_transfer = Transaction.transfer(tx_create.to_inputs(), [([alice.public_key], 100)],
                                       asset_id=tx_create.id)
    tx_transfer_signed = tx_transfer.sign([alice.private_key, user_sk])

    b.store_bulk_transactions([tx_create_signed])

    assert tx_transfer_signed.validate(b) == tx_transfer_signed
    assert len(tx_transfer_signed.outputs) == 1
    assert tx_transfer_signed.outputs[0].amount == 100
    assert len(tx_transfer_signed.inputs) == 2

    ffill_fid0 = _fulfillment_to_details(tx_transfer_signed.inputs[0].fulfillment)
    ffill_fid1 = _fulfillment_to_details(tx_transfer_signed.inputs[1].fulfillment)
    assert 'subconditions' not in ffill_fid0
    assert 'subconditions' in ffill_fid1
    assert len(ffill_fid1['subconditions']) == 2

    b.store_bulk_transactions([tx_transfer_signed])
    with pytest.raises(DoubleSpend):
        tx_transfer_signed.validate(b)


# TRANSFER divisible asset
# Multiple inputs
# Mix: one input with a single owners_before, one input with multiple
#      owners_before
# Multiple outputs
# Mix: one output with a single owners_after, one output with multiple
#      owners_after
def test_muiltiple_in_mix_own_multiple_out_mix_own_transfer(alice, b, user_pk,
                                                            user_sk):
    from bigchaindb.models import Transaction
    from bigchaindb.common.transaction import _fulfillment_to_details

    # CREATE divisible asset
    tx_create = Transaction.create([alice.public_key], [([user_pk], 50), ([user_pk, alice.public_key], 50)],
                                   asset={'name': random.random()})
    tx_create_signed = tx_create.sign([alice.private_key])

    # TRANSFER
    tx_transfer = Transaction.transfer(tx_create.to_inputs(),
                                       [([alice.public_key], 50), ([alice.public_key, user_pk], 50)],
                                       asset_id=tx_create.id)
    tx_transfer_signed = tx_transfer.sign([alice.private_key, user_sk])

    b.store_bulk_transactions([tx_create_signed])

    assert tx_transfer_signed.validate(b) == tx_transfer_signed
    assert len(tx_transfer_signed.outputs) == 2
    assert tx_transfer_signed.outputs[0].amount == 50
    assert tx_transfer_signed.outputs[1].amount == 50
    assert len(tx_transfer_signed.inputs) == 2

    cond_cid0 = tx_transfer_signed.outputs[0].to_dict()
    cond_cid1 = tx_transfer_signed.outputs[1].to_dict()
    assert 'subconditions' not in cond_cid0['condition']['details']
    assert 'subconditions' in cond_cid1['condition']['details']
    assert len(cond_cid1['condition']['details']['subconditions']) == 2

    ffill_fid0 = _fulfillment_to_details(tx_transfer_signed.inputs[0].fulfillment)
    ffill_fid1 = _fulfillment_to_details(tx_transfer_signed.inputs[1].fulfillment)
    assert 'subconditions' not in ffill_fid0
    assert 'subconditions' in ffill_fid1
    assert len(ffill_fid1['subconditions']) == 2

    b.store_bulk_transactions([tx_transfer_signed])
    with pytest.raises(DoubleSpend):
        tx_transfer_signed.validate(b)


# TRANSFER divisible asset
# Multiple inputs from different transactions
# Single owners_before
# Single output
# Single owners_after
def test_multiple_in_different_transactions(alice, b, user_pk, user_sk):
    from bigchaindb.models import Transaction

    # CREATE divisible asset
    # `b` creates a divisible asset and assigns 50 shares to `b` and
    # 50 shares to `user_pk`
    tx_create = Transaction.create([alice.public_key], [([user_pk], 50), ([alice.public_key], 50)],
                                   asset={'name': random.random()})
    tx_create_signed = tx_create.sign([alice.private_key])

    # TRANSFER divisible asset
    # `b` transfers its 50 shares to `user_pk`
    # after this transaction `user_pk` will have a total of 100 shares
    # split across two different transactions
    tx_transfer1 = Transaction.transfer(tx_create.to_inputs([1]),
                                        [([user_pk], 50)],
                                        asset_id=tx_create.id)
    tx_transfer1_signed = tx_transfer1.sign([alice.private_key])

    # TRANSFER
    # `user_pk` combines two different transaction with 50 shares each and
    # transfers a total of 100 shares back to `b`
    tx_transfer2 = Transaction.transfer(tx_create.to_inputs([0]) +
                                        tx_transfer1.to_inputs([0]),
                                        [([alice.private_key], 100)],
                                        asset_id=tx_create.id)
    tx_transfer2_signed = tx_transfer2.sign([user_sk])

    b.store_bulk_transactions([tx_create_signed, tx_transfer1_signed])

    assert tx_transfer2_signed.validate(b) == tx_transfer2_signed
    assert len(tx_transfer2_signed.outputs) == 1
    assert tx_transfer2_signed.outputs[0].amount == 100
    assert len(tx_transfer2_signed.inputs) == 2

    fid0_input = tx_transfer2_signed.inputs[0].fulfills.txid
    fid1_input = tx_transfer2_signed.inputs[1].fulfills.txid
    assert fid0_input == tx_create.id
    assert fid1_input == tx_transfer1.id


# In a TRANSFER transaction of a divisible asset the amount being spent in the
# inputs needs to match the amount being sent in the outputs.
# In other words `amount_in_inputs - amount_in_outputs == 0`
def test_amount_error_transfer(alice, b, user_pk, user_sk):
    from bigchaindb.models import Transaction
    from bigchaindb.common.exceptions import AmountError

    # CREATE divisible asset
    tx_create = Transaction.create([alice.public_key], [([user_pk], 100)], asset={'name': random.random()})
    tx_create_signed = tx_create.sign([alice.private_key])

    b.store_bulk_transactions([tx_create_signed])

    # TRANSFER
    # output amount less than input amount
    tx_transfer = Transaction.transfer(tx_create.to_inputs(), [([alice.public_key], 50)],
                                       asset_id=tx_create.id)
    tx_transfer_signed = tx_transfer.sign([user_sk])

    with pytest.raises(AmountError):
        tx_transfer_signed.validate(b)

    # TRANSFER
    # output amount greater than input amount
    tx_transfer = Transaction.transfer(tx_create.to_inputs(), [([alice.public_key], 101)],
                                       asset_id=tx_create.id)
    tx_transfer_signed = tx_transfer.sign([user_sk])

    with pytest.raises(AmountError):
        tx_transfer_signed.validate(b)


def test_threshold_same_public_key(alice, b, user_pk, user_sk):
    # If we try to fulfill a threshold condition where each subcondition has
    # the same key get_subcondition_from_vk will always return the first
    # subcondition. This means that only the 1st subfulfillment will be
    # generated
    # Creating threshold conditions with the same key does not make sense but
    # that does not mean that the code shouldn't work.

    from bigchaindb.models import Transaction

    # CREATE divisible asset
    tx_create = Transaction.create([alice.public_key], [([user_pk, user_pk], 100)],
                                   asset={'name': random.random()})
    tx_create_signed = tx_create.sign([alice.private_key])

    # TRANSFER
    tx_transfer = Transaction.transfer(tx_create.to_inputs(), [([alice.public_key], 100)],
                                       asset_id=tx_create.id)
    tx_transfer_signed = tx_transfer.sign([user_sk, user_sk])

    b.store_bulk_transactions([tx_create_signed])

    assert tx_transfer_signed.validate(b) == tx_transfer_signed

    b.store_bulk_transactions([tx_transfer_signed])
    with pytest.raises(DoubleSpend):
        tx_transfer_signed.validate(b)


def test_sum_amount(alice, b, user_pk, user_sk):
    from bigchaindb.models import Transaction

    # CREATE divisible asset with 3 outputs with amount 1
    tx_create = Transaction.create([alice.public_key], [([user_pk], 1), ([user_pk], 1), ([user_pk], 1)],
                                   asset={'name': random.random()})
    tx_create_signed = tx_create.sign([alice.private_key])

    # create a transfer transaction with one output and check if the amount
    # is 3
    tx_transfer = Transaction.transfer(tx_create.to_inputs(), [([alice.public_key], 3)],
                                       asset_id=tx_create.id)
    tx_transfer_signed = tx_transfer.sign([user_sk])

    b.store_bulk_transactions([tx_create_signed])

    assert tx_transfer_signed.validate(b) == tx_transfer_signed
    assert len(tx_transfer_signed.outputs) == 1
    assert tx_transfer_signed.outputs[0].amount == 3

    b.store_bulk_transactions([tx_transfer_signed])
    with pytest.raises(DoubleSpend):
        tx_transfer_signed.validate(b)


def test_divide(alice, b, user_pk, user_sk):
    from bigchaindb.models import Transaction

    # CREATE divisible asset with 1 output with amount 3
    tx_create = Transaction.create([alice.public_key], [([user_pk], 3)], asset={'name': random.random()})
    tx_create_signed = tx_create.sign([alice.private_key])

    # create a transfer transaction with 3 outputs and check if the amount
    # of each output is 1
    tx_transfer = Transaction.transfer(tx_create.to_inputs(),
                                       [([alice.public_key], 1), ([alice.public_key], 1), ([alice.public_key], 1)],
                                       asset_id=tx_create.id)
    tx_transfer_signed = tx_transfer.sign([user_sk])

    b.store_bulk_transactions([tx_create_signed])

    assert tx_transfer_signed.validate(b) == tx_transfer_signed
    assert len(tx_transfer_signed.outputs) == 3
    for output in tx_transfer_signed.outputs:
        assert output.amount == 1

    b.store_bulk_transactions([tx_transfer_signed])
    with pytest.raises(DoubleSpend):
        tx_transfer_signed.validate(b)
