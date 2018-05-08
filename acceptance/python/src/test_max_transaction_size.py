# # Transaction Size Tes
# BigchainDB allows to limit the maximum size of a transaction. This acceptance
# test make sure that this is happening.

import os

import pytest
import requests

from bigchaindb_driver import exceptions, BigchainDB
from bigchaindb_driver.crypto import generate_keypair

## Helper functions

# Helper function to normalize the URL to connect to a BigchainDB node.
def normalize_url(url):
    from urllib.parse import urlparse, urlunparse
    if '://' not in url:
        url = 'http://' + url
    p = urlparse(url)
    if not p.port:
        p = p._replace(netloc=p.hostname + ':9984')
    return urlunparse(p)


BIGCHAINDB_ENDPOINT = normalize_url(os.environ.get('BIGCHAINDB_ENDPOINT', 'http://localhost:9984'))
bdb = BigchainDB(BIGCHAINDB_ENDPOINT)


# Helper function to generate a transaction with an approximated size. Note
# that the final size of the transaction will be bigger, since this function
# does not consider the size of all other fields of the transaction model such
# as `id`, `inputs`, `outputs`, and more.
def generate_transaction_by_size(size):
    keypair = generate_keypair()

    asset = {'data': {'_': 'x' * size}}

    prepared_creation_tx = bdb.transactions.prepare(
            operation='CREATE',
            signers=keypair.public_key,
            asset=asset)

    fulfilled_creation_tx = bdb.transactions.fulfill(
            prepared_creation_tx,
            private_keys=keypair.private_key)

    return fulfilled_creation_tx

## Testing time!
def test_max_transaction_size():
    # First, we retrieve the maximum size of a transaction from the API.
    max_transaction_size = requests.get(BIGCHAINDB_ENDPOINT).json()['max_transaction_size']

    # We then generate a first, valid transaction, and verify that it has been
    # accepted.
    transaction = generate_transaction_by_size(1)
    sent_transfer_tx = bdb.transactions.send(transaction)
    assert bdb.transactions.retrieve(transaction['id']) == sent_transfer_tx

    # Now we generate another transaction, double the size of the allowed upper
    # bound.
    transaction = generate_transaction_by_size(max_transaction_size * 2)
    try:
        sent_transfer_tx = bdb.transactions.send(transaction)
    except exceptions.TransportError as e:
        # We expect an exception with status code `413`, that is **Entity too
        # large**.
        assert e.status_code == 413

    # Just to be 100% sure, we also check that the transaction has not been
    # stored in BigchainDB.
    with pytest.raises(exceptions.NotFoundError):
        assert bdb.transactions.retrieve(transaction['id'])

    # Now let's play the 1337 h4x0r card. We generate another transaction
    # double the size of the allowed limit first.
    transaction = generate_transaction_by_size(max_transaction_size * 2)

    # Then we handcraft an HTTP request and we spoof the `Content-Length` header, saying
    # that the total size of the request is just one byte. (Make sure to wear
    # leather gloves to not leave your fingerprints on the keyboard, you don't
    # want NSA to catch you!)
    req = requests.post(
        BIGCHAINDB_ENDPOINT + '/api/v1/transactions?mode=commit',
        json=transaction,
        headers={'Content-Length': '1'})

    # This should fail as well, so we check that we get a `413` and no
    # transaction has been stored in BigchainDB.
    assert req.status_code == 413
    with pytest.raises(exceptions.NotFoundError):
        assert bdb.transactions.retrieve(transaction['id'])
