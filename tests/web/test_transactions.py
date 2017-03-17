import json
from unittest.mock import patch

import pytest
from bigchaindb.common import crypto


TX_ENDPOINT = '/api/v1/transactions/'


@pytest.mark.bdb
@pytest.mark.usefixtures('inputs')
def test_get_transaction_endpoint(b, client, user_pk):
    input_tx = b.get_owned_ids(user_pk).pop()
    tx = b.get_transaction(input_tx.txid)
    res = client.get(TX_ENDPOINT + tx.id)
    assert tx.to_dict() == res.json
    assert res.status_code == 200


@pytest.mark.bdb
@pytest.mark.usefixtures('inputs')
def test_get_transaction_returns_404_if_not_found(client):
    res = client.get(TX_ENDPOINT + '123')
    assert res.status_code == 404

    res = client.get(TX_ENDPOINT + '123/')
    assert res.status_code == 404


@pytest.mark.bdb
def test_post_create_transaction_endpoint(b, client):
    from bigchaindb.models import Transaction
    user_priv, user_pub = crypto.generate_key_pair()

    tx = Transaction.create([user_pub], [([user_pub], 1)])
    tx = tx.sign([user_priv])

    res = client.post(TX_ENDPOINT, data=json.dumps(tx.to_dict()))

    assert res.status_code == 202

    assert res.json['inputs'][0]['owners_before'][0] == user_pub
    assert res.json['outputs'][0]['public_keys'][0] == user_pub


def test_post_create_transaction_with_invalid_id(b, client, caplog):
    from bigchaindb.common.exceptions import InvalidHash
    from bigchaindb.models import Transaction
    user_priv, user_pub = crypto.generate_key_pair()

    tx = Transaction.create([user_pub], [([user_pub], 1)])
    tx = tx.sign([user_priv]).to_dict()
    tx['id'] = 'abcd' * 16

    res = client.post(TX_ENDPOINT, data=json.dumps(tx))
    expected_status_code = 400
    expected_error_message = (
        'Invalid transaction ({}): The transaction\'s id \'{}\' isn\'t equal to '
        'the hash of its body, i.e. it\'s not valid.'
    ).format(InvalidHash.__name__, tx['id'])
    assert res.status_code == expected_status_code
    assert res.json['message'] == expected_error_message
    assert caplog.records[0].args['status'] == expected_status_code
    assert caplog.records[0].args['message'] == expected_error_message


def test_post_create_transaction_with_invalid_signature(b, client, caplog):
    from bigchaindb.common.exceptions import InvalidSignature
    from bigchaindb.models import Transaction
    user_priv, user_pub = crypto.generate_key_pair()

    tx = Transaction.create([user_pub], [([user_pub], 1)])
    tx = tx.sign([user_priv]).to_dict()
    tx['inputs'][0]['fulfillment'] = 'cf:0:0'

    res = client.post(TX_ENDPOINT, data=json.dumps(tx))
    expected_status_code = 400
    expected_error_message = (
        'Invalid transaction ({}): Fulfillment URI '
        'couldn\'t been parsed'
    ).format(InvalidSignature.__name__)
    assert res.status_code == expected_status_code
    assert res.json['message'] == expected_error_message
    assert caplog.records[0].args['status'] == expected_status_code
    assert caplog.records[0].args['message'] == expected_error_message


def test_post_create_transaction_with_invalid_structure(client):
    res = client.post(TX_ENDPOINT, data='{}')
    assert res.status_code == 400


def test_post_create_transaction_with_invalid_schema(client, caplog):
    from bigchaindb.models import Transaction
    user_priv, user_pub = crypto.generate_key_pair()
    tx = Transaction.create(
        [user_pub], [([user_pub], 1)]).sign([user_priv]).to_dict()
    del tx['version']
    res = client.post(TX_ENDPOINT, data=json.dumps(tx))
    expected_status_code = 400
    expected_error_message = (
        "Invalid transaction schema: 'version' is a required property")
    assert res.status_code == expected_status_code
    assert res.json['message'] == expected_error_message
    assert caplog.records[0].args['status'] == expected_status_code
    assert caplog.records[0].args['message'] == expected_error_message


@pytest.mark.parametrize('exc,msg', (
    ('AmountError', 'Do the math again!'),
    ('DoubleSpend', 'Nope! It is gone now!'),
    ('InvalidHash', 'Do not smoke that!'),
    ('InvalidSignature', 'Falsche Unterschrift!'),
    ('ValidationError', 'Create and transfer!'),
    ('InputDoesNotExist', 'Hallucinations?'),
    ('TransactionOwnerError', 'Not yours!'),
    ('TransactionNotInValidBlock', 'Wait, maybe?'),
    ('ValidationError', '?'),
))
def test_post_invalid_transaction(client, exc, msg, monkeypatch, caplog):
    from bigchaindb.common import exceptions
    exc_cls = getattr(exceptions, exc)

    def mock_validation(self_, tx):
        raise exc_cls(msg)

    monkeypatch.setattr(
        'bigchaindb.Bigchain.validate_transaction', mock_validation)
    monkeypatch.setattr(
        'bigchaindb.models.Transaction.from_dict', lambda tx: None)
    res = client.post(TX_ENDPOINT, data=json.dumps({}))
    expected_status_code = 400
    expected_error_message = 'Invalid transaction ({}): {}'.format(exc, msg)
    assert res.status_code == expected_status_code
    assert (res.json['message'] ==
            'Invalid transaction ({}): {}'.format(exc, msg))
    assert caplog.records[2].args['status'] == expected_status_code
    assert caplog.records[2].args['message'] == expected_error_message


@pytest.mark.bdb
@pytest.mark.usefixtures('inputs')
def test_post_transfer_transaction_endpoint(b, client, user_pk, user_sk):
    sk, pk = crypto.generate_key_pair()
    from bigchaindb.models import Transaction

    user_priv, user_pub = crypto.generate_key_pair()

    input_valid = b.get_owned_ids(user_pk).pop()
    create_tx = b.get_transaction(input_valid.txid)
    transfer_tx = Transaction.transfer(create_tx.to_inputs(),
                                       [([user_pub], 1)],
                                       asset_id=create_tx.id)
    transfer_tx = transfer_tx.sign([user_sk])

    res = client.post(TX_ENDPOINT, data=json.dumps(transfer_tx.to_dict()))

    assert res.status_code == 202

    assert res.json['inputs'][0]['owners_before'][0] == user_pk
    assert res.json['outputs'][0]['public_keys'][0] == user_pub


@pytest.mark.bdb
@pytest.mark.usefixtures('inputs')
def test_post_invalid_transfer_transaction_returns_400(b, client, user_pk):
    from bigchaindb.models import Transaction
    from bigchaindb.common.exceptions import InvalidSignature

    user_pub = crypto.generate_key_pair()[1]

    input_valid = b.get_owned_ids(user_pk).pop()
    create_tx = b.get_transaction(input_valid.txid)
    transfer_tx = Transaction.transfer(create_tx.to_inputs(),
                                       [([user_pub], 1)],
                                       asset_id=create_tx.id)

    res = client.post(TX_ENDPOINT, data=json.dumps(transfer_tx.to_dict()))
    expected_status_code = 400
    expected_error_message = 'Invalid transaction ({}): {}'.format(
        InvalidSignature.__name__, 'Transaction signature is invalid.')
    assert res.status_code == expected_status_code
    assert res.json['message'] == expected_error_message


def test_transactions_get_list_good(client):
    from functools import partial

    def get_txs_patched(conn, **args):
        """ Patch `get_transactions_filtered` so that rather than return an array
            of transactions it returns an array of shims with a to_dict() method
            that reports one of the arguments passed to `get_transactions_filtered`.
            """
        return [type('', (), {'to_dict': partial(lambda a: a, arg)})
                for arg in sorted(args.items())]

    asset_id = '1' * 64

    with patch('bigchaindb.core.Bigchain.get_transactions_filtered', get_txs_patched):
        url = TX_ENDPOINT + '?asset_id=' + asset_id
        assert client.get(url).json == [
            ['asset_id', asset_id],
            ['operation', None]
        ]
        url = TX_ENDPOINT + '?asset_id=' + asset_id + '&operation=CREATE'
        assert client.get(url).json == [
            ['asset_id', asset_id],
            ['operation', 'CREATE']
        ]


def test_transactions_get_list_bad(client):
    def should_not_be_called():
        assert False
    with patch('bigchaindb.core.Bigchain.get_transactions_filtered',
               lambda *_, **__: should_not_be_called()):
        # Test asset id validated
        url = TX_ENDPOINT + '?asset_id=' + '1' * 63
        assert client.get(url).status_code == 400
        # Test operation validated
        url = TX_ENDPOINT + '?asset_id=' + '1' * 64 + '&operation=CEATE'
        assert client.get(url).status_code == 400
        # Test asset ID required
        url = TX_ENDPOINT + '?operation=CREATE'
        assert client.get(url).status_code == 400
