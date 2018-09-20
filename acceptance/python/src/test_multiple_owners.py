# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

# # Multiple owners integration testing
# This test checks if we can successfully create and transfer a transaction
# with multiple owners.
# The script tests various things like:
#
# - create a transaction with multiple owners
# - check if the transaction is stored and has the right amount of public keys
# - transfer the transaction to a third person
#
# We run a series of checks for each step, that is retrieving
# the transaction from the remote system, and also checking the public keys
# of a given transaction.
#
# This integration test is a rip-off of our
# [tutorial](https://docs.bigchaindb.com/projects/py-driver/en/latest/usage.html).

# ## Imports
# We need some utils from the `os` package, we will interact with
# env variables.
import os

# For this test case we import and use the Python Driver.
from bigchaindb_driver import BigchainDB
from bigchaindb_driver.crypto import generate_keypair


def test_multiple_owners():
    # ## Set up a connection to BigchainDB
    # Check [test_basic.py](./test_basic.html) to get some more details
    # about the endpoint.
    bdb = BigchainDB(os.environ.get('BIGCHAINDB_ENDPOINT'))

    # Hey Alice and Bob, nice to see you again!
    alice, bob = generate_keypair(), generate_keypair()

    # ## Alice and Bob create a transaction
    # Alice and Bob just moved into a shared flat, no one can afford these
    # high rents anymore. Bob suggests to get a dish washer for the
    # kitchen. Alice agrees and here they go, creating the asset for their
    # dish washer.
    dw_asset = {
        'data': {
            'dish washer': {
                'serial_number': 1337
            }
        }
    }

    # They prepare a `CREATE` transaction. To have multiple owners, both
    # Bob and Alice need to be the recipients.
    prepared_dw_tx = bdb.transactions.prepare(
        operation='CREATE',
        signers=alice.public_key,
        recipients=(alice.public_key, bob.public_key),
        asset=dw_asset)

    # Now they both sign the transaction by providing their private keys.
    # And send it afterwards.
    fulfilled_dw_tx = bdb.transactions.fulfill(
        prepared_dw_tx,
        private_keys=[alice.private_key, bob.private_key])

    bdb.transactions.send_commit(fulfilled_dw_tx)

    # We store the `id` of the transaction to use it later on.
    dw_id = fulfilled_dw_tx['id']

    # Let's check if the transaction was successful.
    assert bdb.transactions.retrieve(dw_id), \
        'Cannot find transaction {}'.format(dw_id)

    # The transaction should have two public keys in the outputs.
    assert len(
        bdb.transactions.retrieve(dw_id)['outputs'][0]['public_keys']) == 2

    # ## Alice and Bob transfer a transaction to Carol.
    # Alice and Bob save a lot of money living together. They often go out
    # for dinner and don't cook at home. But now they don't have any dishes to
    # wash, so they decide to sell the dish washer to their friend Carol.

    # Hey Carol, nice to meet you!
    carol = generate_keypair()

    # Alice and Bob prepare the transaction to transfer the dish washer to
    # Carol.
    transfer_asset = {'id': dw_id}

    output_index = 0
    output = fulfilled_dw_tx['outputs'][output_index]
    transfer_input = {'fulfillment': output['condition']['details'],
                      'fulfills': {'output_index': output_index,
                                   'transaction_id': fulfilled_dw_tx[
                                       'id']},
                      'owners_before': output['public_keys']}

    # Now they create the transaction...
    prepared_transfer_tx = bdb.transactions.prepare(
        operation='TRANSFER',
        asset=transfer_asset,
        inputs=transfer_input,
        recipients=carol.public_key)

    # ... and sign it with their private keys, then send it.
    fulfilled_transfer_tx = bdb.transactions.fulfill(
        prepared_transfer_tx,
        private_keys=[alice.private_key, bob.private_key])

    sent_transfer_tx = bdb.transactions.send_commit(fulfilled_transfer_tx)

    # They check if the transaction was successful.
    assert bdb.transactions.retrieve(
        fulfilled_transfer_tx['id']) == sent_transfer_tx

    # The owners before should include both Alice and Bob.
    assert len(
        bdb.transactions.retrieve(fulfilled_transfer_tx['id'])['inputs'][0][
            'owners_before']) == 2

    # While the new owner is Carol.
    assert bdb.transactions.retrieve(fulfilled_transfer_tx['id'])[
           'outputs'][0]['public_keys'][0] == carol.public_key
