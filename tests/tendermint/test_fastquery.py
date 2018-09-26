# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

import pytest

from bigchaindb.common.transaction import TransactionLink
from bigchaindb.models import Transaction


pytestmark = pytest.mark.bdb


@pytest.fixture
def txns(b, user_pk, user_sk, user2_pk, user2_sk):
    txs = [Transaction.create([user_pk], [([user2_pk], 1)]).sign([user_sk]),
           Transaction.create([user2_pk], [([user_pk], 1)]).sign([user2_sk]),
           Transaction.create([user_pk], [([user_pk], 1), ([user2_pk], 1)])
           .sign([user_sk])]
    b.store_bulk_transactions(txs)
    return txs


def test_get_outputs_by_public_key(b, user_pk, user2_pk, txns):
    assert b.fastquery.get_outputs_by_public_key(user_pk) == [
        TransactionLink(txns[1].id, 0),
        TransactionLink(txns[2].id, 0)
    ]
    assert b.fastquery.get_outputs_by_public_key(user2_pk) == [
        TransactionLink(txns[0].id, 0),
        TransactionLink(txns[2].id, 1),
    ]


def test_filter_spent_outputs(b, user_pk, user_sk):
    out = [([user_pk], 1)]
    tx1 = Transaction.create([user_pk], out * 2)
    tx1.sign([user_sk])

    inputs = tx1.to_inputs()

    tx2 = Transaction.transfer([inputs[0]], out, tx1.id)
    tx2.sign([user_sk])

    # tx2 produces a new unspent. inputs[1] remains unspent.
    b.store_bulk_transactions([tx1, tx2])

    outputs = b.fastquery.get_outputs_by_public_key(user_pk)
    unspents = b.fastquery.filter_spent_outputs(outputs)

    assert set(unsp for unsp in unspents) == {
        inputs[1].fulfills,
        tx2.to_inputs()[0].fulfills,
    }


def test_filter_unspent_outputs(b, user_pk, user_sk):
    out = [([user_pk], 1)]
    tx1 = Transaction.create([user_pk], out * 2)
    tx1.sign([user_sk])

    inputs = tx1.to_inputs()

    tx2 = Transaction.transfer([inputs[0]], out, tx1.id)
    tx2.sign([user_sk])

    # tx2 produces a new unspent. input[1] remains unspent.
    b.store_bulk_transactions([tx1, tx2])

    outputs = b.fastquery.get_outputs_by_public_key(user_pk)
    spents = b.fastquery.filter_unspent_outputs(outputs)

    assert set(sp for sp in spents) == {
        inputs[0].fulfills,
    }


def test_outputs_query_key_order(b, user_pk, user_sk, user2_pk, user2_sk):
    from bigchaindb import backend
    from bigchaindb.backend import connect

    tx1 = Transaction.create([user_pk],
                             [([user_pk], 3), ([user_pk], 2), ([user_pk], 1)])\
                     .sign([user_sk])
    b.store_bulk_transactions([tx1])

    inputs = tx1.to_inputs()
    tx2 = Transaction.transfer([inputs[1]], [([user2_pk], 2)], tx1.id).sign([user_sk])
    assert tx2.validate(b)

    tx2_dict = tx2.to_dict()
    fulfills = tx2_dict['inputs'][0]['fulfills']
    tx2_dict['inputs'][0]['fulfills'] = {'transaction_id': fulfills['transaction_id'],
                                         'output_index': fulfills['output_index']}
    backend.query.store_transactions(b.connection, [tx2_dict])

    outputs = b.get_outputs_filtered(user_pk, spent=False)
    assert len(outputs) == 2

    outputs = b.get_outputs_filtered(user2_pk, spent=False)
    assert len(outputs) == 1

    # clean the transaction, metdata and asset collection
    conn = connect()
    conn.run(conn.collection('transactions').delete_many({}))
    conn.run(conn.collection('metadata').delete_many({}))
    conn.run(conn.collection('assets').delete_many({}))

    b.store_bulk_transactions([tx1])
    tx2_dict = tx2.to_dict()
    tx2_dict['inputs'][0]['fulfills'] = {'output_index': fulfills['output_index'],
                                         'transaction_id': fulfills['transaction_id']}

    backend.query.store_transactions(b.connection, [tx2_dict])
    outputs = b.get_outputs_filtered(user_pk, spent=False)
    assert len(outputs) == 2

    outputs = b.get_outputs_filtered(user2_pk, spent=False)
    assert len(outputs) == 1
