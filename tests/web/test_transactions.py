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

    assert '../statuses?transaction_id={}'.format(tx.id) in \
        res.headers['Location']

    assert res.json['inputs'][0]['owners_before'][0] == user_pub
    assert res.json['outputs'][0]['public_keys'][0] == user_pub


@pytest.mark.parametrize("nested", [False, True])
@pytest.mark.parametrize("language,expected_status_code", [
    ('danish', 202), ('dutch', 202), ('english', 202), ('finnish', 202),
    ('french', 202), ('german', 202), ('hungarian', 202), ('italian', 202),
    ('norwegian', 202), ('portuguese', 202), ('romanian', 202), ('none', 202),
    ('russian', 202), ('spanish', 202), ('swedish', 202), ('turkish', 202),
    ('da', 202), ('nl', 202), ('en', 202), ('fi', 202), ('fr', 202),
    ('de', 202), ('hu', 202), ('it', 202), ('nb', 202), ('pt', 202),
    ('ro', 202), ('ru', 202), ('es', 202), ('sv', 202), ('tr', 202),
    ('any', 400)
])
@pytest.mark.language
@pytest.mark.bdb
def test_post_create_transaction_with_language(b, client, nested, language,
                                               expected_status_code):
    from bigchaindb.models import Transaction
    from bigchaindb.backend.mongodb.connection import MongoDBConnection

    if isinstance(b.connection, MongoDBConnection):
        user_priv, user_pub = crypto.generate_key_pair()
        lang_obj = {'language': language}

        if nested:
            asset = {'root': lang_obj}
        else:
            asset = lang_obj

        tx = Transaction.create([user_pub], [([user_pub], 1)],
                                asset=asset)
        tx = tx.sign([user_priv])
        res = client.post(TX_ENDPOINT, data=json.dumps(tx.to_dict()))
        assert res.status_code == expected_status_code
        if res.status_code == 400:
            expected_error_message = (
                'Invalid transaction (ValidationError): MongoDB does not support '
                'text search for the language "{}". If you do not understand this '
                'error message then please rename key/field "language" to something '
                'else like "lang".').format(language)
            assert res.json['message'] == expected_error_message


@pytest.mark.parametrize("field", ['asset', 'metadata'])
@pytest.mark.parametrize("value,err_key,expected_status_code", [
    ({'bad.key': 'v'}, 'bad.key', 400),
    ({'$bad.key': 'v'}, '$bad.key', 400),
    ({'$badkey': 'v'}, '$badkey', 400),
    ({'bad\x00key': 'v'}, 'bad\x00key', 400),
    ({'good_key': {'bad.key': 'v'}}, 'bad.key', 400),
    ({'good_key': 'v'}, 'good_key', 202)
])
@pytest.mark.bdb
def test_post_create_transaction_with_invalid_key(b, client, field, value,
                                                  err_key, expected_status_code):
    from bigchaindb.models import Transaction
    from bigchaindb.backend.mongodb.connection import MongoDBConnection
    user_priv, user_pub = crypto.generate_key_pair()

    if isinstance(b.connection, MongoDBConnection):
        if field == 'asset':
            tx = Transaction.create([user_pub], [([user_pub], 1)],
                                    asset=value)
        elif field == 'metadata':
            tx = Transaction.create([user_pub], [([user_pub], 1)],
                                    metadata=value)
        tx = tx.sign([user_priv])
        res = client.post(TX_ENDPOINT, data=json.dumps(tx.to_dict()))

        assert res.status_code == expected_status_code
        if res.status_code == 400:
            expected_error_message = (
                'Invalid transaction (ValidationError): Invalid key name "{}" '
                'in {} object. The key name cannot contain characters '
                '".", "$" or null characters').format(err_key, field)
            assert res.json['message'] == expected_error_message


@patch('bigchaindb.web.views.base.logger')
def test_post_create_transaction_with_invalid_id(mock_logger, b, client):
    from bigchaindb.common.exceptions import InvalidHash
    from bigchaindb.models import Transaction
    user_priv, user_pub = crypto.generate_key_pair()

    tx = Transaction.create([user_pub], [([user_pub], 1)])
    tx = tx.sign([user_priv]).to_dict()
    tx['id'] = 'abcd' * 16

    res = client.post(TX_ENDPOINT, data=json.dumps(tx))
    expected_status_code = 400
    expected_error_message = (
        "Invalid transaction ({}): The transaction's id '{}' isn't equal to "
        "the hash of its body, i.e. it's not valid."
    ).format(InvalidHash.__name__, tx['id'])
    assert res.status_code == expected_status_code
    assert res.json['message'] == expected_error_message
    assert mock_logger.error.called
    assert (
        'HTTP API error: %(status)s - %(method)s:%(path)s - %(message)s' in
        mock_logger.error.call_args[0]
    )
    assert (
        {
            'message': expected_error_message, 'status': expected_status_code,
            'method': 'POST', 'path': TX_ENDPOINT
        } in mock_logger.error.call_args[0]
    )
    # TODO put back caplog based asserts once possible
    # assert caplog.records[0].args['status'] == expected_status_code
    # assert caplog.records[0].args['message'] == expected_error_message


@patch('bigchaindb.web.views.base.logger')
def test_post_create_transaction_with_invalid_signature(mock_logger,
                                                        b,
                                                        client):
    from bigchaindb.common.exceptions import InvalidSignature
    from bigchaindb.models import Transaction
    user_priv, user_pub = crypto.generate_key_pair()

    tx = Transaction.create([user_pub], [([user_pub], 1)])
    tx = tx.sign([user_priv]).to_dict()
    tx['inputs'][0]['fulfillment'] = 64 * '0'

    res = client.post(TX_ENDPOINT, data=json.dumps(tx))
    expected_status_code = 400
    expected_error_message = (
        'Invalid transaction ({}): Fulfillment URI '
        'couldn\'t been parsed'
    ).format(InvalidSignature.__name__)
    assert res.status_code == expected_status_code
    assert res.json['message'] == expected_error_message
    assert mock_logger.error.called
    assert (
        'HTTP API error: %(status)s - %(method)s:%(path)s - %(message)s' in
        mock_logger.error.call_args[0]
    )
    assert (
        {
            'message': expected_error_message, 'status': expected_status_code,
            'method': 'POST', 'path': TX_ENDPOINT
        } in mock_logger.error.call_args[0]
    )
    # TODO put back caplog based asserts once possible
    # assert caplog.records[0].args['status'] == expected_status_code
    # assert caplog.records[0].args['message'] == expected_error_message


def test_post_create_transaction_with_invalid_structure(client):
    res = client.post(TX_ENDPOINT, data='{}')
    assert res.status_code == 400


@patch('bigchaindb.web.views.base.logger')
def test_post_create_transaction_with_invalid_schema(mock_logger, client):
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
    assert mock_logger.error.called
    assert (
        'HTTP API error: %(status)s - %(method)s:%(path)s - %(message)s' in
        mock_logger.error.call_args[0]
    )
    assert (
        {
            'message': expected_error_message, 'status': expected_status_code,
            'method': 'POST', 'path': TX_ENDPOINT
        } in mock_logger.error.call_args[0]
    )
    # TODO put back caplog based asserts once possible
    # assert caplog.records[0].args['status'] == expected_status_code
    # assert caplog.records[0].args['message'] == expected_error_message


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
@patch('bigchaindb.web.views.base.logger')
def test_post_invalid_transaction(mock_logger, client, exc, msg, monkeypatch,):
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
    assert mock_logger.error.called
    assert (
        'HTTP API error: %(status)s - %(method)s:%(path)s - %(message)s' in
        mock_logger.error.call_args[0]
    )
    assert (
        {
            'message': expected_error_message, 'status': expected_status_code,
            'method': 'POST', 'path': TX_ENDPOINT
        } in mock_logger.error.call_args[0]
    )
    # TODO put back caplog based asserts once possible
    # assert caplog.records[2].args['status'] == expected_status_code
    # assert caplog.records[2].args['message'] == expected_error_message


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


def test_return_only_valid_transaction(client):
    from bigchaindb import Bigchain

    def get_transaction_patched(status):
        def inner(self, tx_id, include_status):
            return {}, status
        return inner

    # NOTE: `get_transaction` only returns a transaction if it's included in an
    #       UNDECIDED or VALID block, as well as transactions from the backlog.
    #       As the endpoint uses `get_transaction`, we don't have to test
    #       against invalid transactions here.
    with patch('bigchaindb.core.Bigchain.get_transaction',
               get_transaction_patched(Bigchain.TX_UNDECIDED)):
        url = '{}{}'.format(TX_ENDPOINT, '123')
        assert client.get(url).status_code == 404

    with patch('bigchaindb.core.Bigchain.get_transaction',
               get_transaction_patched(Bigchain.TX_IN_BACKLOG)):
        url = '{}{}'.format(TX_ENDPOINT, '123')
        assert client.get(url).status_code == 404
