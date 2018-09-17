# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

# ## Testing potentially hazardous strings
# This test uses a library of `naughty` strings (code injections, weird unicode chars., etc.) as both keys and values.
# We look for either a successful tx, or in the case that we use a naughty string as a key, and it violates some key
# constraints, we expect to receive a well formatted error message.

# ## Imports
# We need some utils from the `os` package, we will interact with
# env variables.
import os

# Since the naughty strings get encoded and decoded in odd ways,
# we'll use a regex to sweep those details under the rug.
import re

# We'll use a nice library of naughty strings...
from blns import blns

# And parameterize our test so each one is treated as a separate test case
import pytest

# For this test case we import and use the Python Driver.
from bigchaindb_driver import BigchainDB
from bigchaindb_driver.crypto import generate_keypair
from bigchaindb_driver.exceptions import BadRequest

naughty_strings = blns.all()


# This is our base test case, but we'll reuse it to send naughty strings as both keys and values.
def send_naughty_tx(asset, metadata):
    # ## Set up a connection to BigchainDB
    # Check [test_basic.py](./test_basic.html) to get some more details
    # about the endpoint.
    bdb = BigchainDB(os.environ.get('BIGCHAINDB_ENDPOINT'))

    # Here's Alice.
    alice = generate_keypair()

    # Alice is in a naughty mood today, so she creates a tx with some naughty strings
    prepared_transaction = bdb.transactions.prepare(
        operation='CREATE',
        signers=alice.public_key,
        asset=asset,
        metadata=metadata)

    # She fulfills the transaction
    fulfilled_transaction = bdb.transactions.fulfill(
        prepared_transaction,
        private_keys=alice.private_key)

    # The fulfilled tx gets sent to the BDB network
    try:
        sent_transaction = bdb.transactions.send_commit(fulfilled_transaction)
    except BadRequest as e:
        sent_transaction = e

    # If her key contained a '.', began with a '$', or contained a NUL character
    regex = '.*\..*|\$.*|.*\x00.*'
    key = next(iter(metadata))
    if re.match(regex, key):
        # Then she expects a nicely formatted error code
        status_code = sent_transaction.status_code
        error = sent_transaction.error
        regex = '\{"message":"Invalid transaction \\(ValidationError\\): Invalid key name .* in asset object. ' \
                'The key name cannot contain characters .* or null characters","status":400\}\n'
        assert status_code == 400
        assert re.fullmatch(regex, error), sent_transaction
    # Otherwise, she expects to see her transaction in the database
    elif 'id' in sent_transaction.keys():
        tx_id = sent_transaction['id']
        assert bdb.transactions.retrieve(tx_id)
    # If neither condition was true, then something weird happened...
    else:
        raise TypeError(sent_transaction)


@pytest.mark.parametrize("naughty_string", naughty_strings, ids=naughty_strings)
def test_naughty_keys(naughty_string):

    asset = {'data': {naughty_string: 'nice_value'}}
    metadata = {naughty_string: 'nice_value'}

    send_naughty_tx(asset, metadata)


@pytest.mark.parametrize("naughty_string", naughty_strings, ids=naughty_strings)
def test_naughty_values(naughty_string):

    asset = {'data': {'nice_key': naughty_string}}
    metadata = {'nice_key': naughty_string}

    send_naughty_tx(asset, metadata)
