# TODO: Make sense of this test
def test_init_transaction(b, user_vk):
    from bigchaindb.transaction import (
        Fulfillment,
        Condition,
        Transaction,
        TransactionType,
    )
    from bigchaindb.util import validate_fulfillments

    ffill = Fulfillment([user_vk])
    cond = Condition([user_vk])
    tx = Transaction([ffill], [cond], TransactionType.CREATE)
    tx = tx.to_dict()

    assert tx['transaction']['fulfillments'][0]['owners_before'][0] == b.me
    # NOTE: Why are we accessing `['']`?
    assert tx['transaction']['conditions'][0][''][0] == user_vk
    assert validate_fulfillments(tx)


def test_create_tx_with_empty_inputs():
    from bigchaindb.transaction import (
        Fulfillment,
        Condition,
        Transaction,
        TransactionType,
    )

    ffill = Fulfillment(None)
    cond = Condition(None)
    tx = Transaction([ffill], [cond], TransactionType.CREATE).to_dict()
    assert 'id' in tx
    assert 'transaction' in tx
    assert 'version' in tx
    assert 'fulfillments' in tx['transaction']
    assert 'conditions' in tx['transaction']
    assert 'operation' in tx['transaction']
    assert 'timestamp' in tx['transaction']
    assert 'data' in tx['transaction']
    assert len(tx['transaction']['fulfillments']) == 1
    assert tx['transaction']['fulfillments'][0] == {
        'owners_before': [], 'input': None, 'fulfillment': None, 'fid': 0}
