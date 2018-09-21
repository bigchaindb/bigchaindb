# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

# # Basic Acceptance Test
# Here we check that the primitives of the system behave as expected.
# As you will see, this script tests basic stuff like:
#
# - create a transaction
# - check if the transaction is stored
# - check for the outputs of a given public key
# - transfer the transaction to another key
#
# We run a series of checks for each steps, that is retrieving the transaction from
# the remote system, and also checking the `outputs` of a given public key.
#
# This acceptance test is a rip-off of our
# [tutorial](https://docs.bigchaindb.com/projects/py-driver/en/latest/usage.html).

# ## Imports
# We need some utils from the `os` package, we will interact with
# env variables.
import os

# For this test case we import and use the Python Driver.
from bigchaindb_driver import BigchainDB
from bigchaindb_driver.crypto import generate_keypair


def test_basic():
    # ## Set up a connection to BigchainDB
    # To use BighainDB we need a connection. Here we create one. By default we
    # connect to localhost, but you can override this value using the env variable
    # called `BIGCHAINDB_ENDPOINT`, a valid value must include the schema:
    # `https://example.com:9984`
    bdb = BigchainDB(os.environ.get('BIGCHAINDB_ENDPOINT'))

    # ## Create keypairs
    # This test requires the interaction between two actors with their own keypair.
    # The two keypairs will be called—drum roll—Alice and Bob.
    alice, bob = generate_keypair(), generate_keypair()

    # ## Alice registers her bike in BigchainDB
    # Alice has a nice bike, and here she creates the "digital twin"
    # of her bike.
    bike = {'data': {'bicycle': {'serial_number': 420420}}}

    # She prepares a `CREATE` transaction...
    prepared_creation_tx = bdb.transactions.prepare(
            operation='CREATE',
            signers=alice.public_key,
            asset=bike)

    # ... and she fulfills it with her private key.
    fulfilled_creation_tx = bdb.transactions.fulfill(
            prepared_creation_tx,
            private_keys=alice.private_key)

    # We will use the `id` of this transaction several time, so we store it in
    # a variable with a short and easy name
    bike_id = fulfilled_creation_tx['id']

    # Now she is ready to send it to the BigchainDB Network.
    sent_transfer_tx = bdb.transactions.send_commit(fulfilled_creation_tx)

    # And just to be 100% sure, she also checks if she can retrieve
    # it from the BigchainDB node.
    assert bdb.transactions.retrieve(bike_id), 'Cannot find transaction {}'.format(bike_id)

    # Alice is now the proud owner of one unspent asset.
    assert len(bdb.outputs.get(alice.public_key, spent=False)) == 1
    assert bdb.outputs.get(alice.public_key)[0]['transaction_id'] == bike_id

    # ## Alice transfers her bike to Bob
    # After registering her bike, Alice is ready to transfer it to Bob.
    # She needs to create a new `TRANSFER` transaction.

    # A `TRANSFER` transaction contains a pointer to the original asset. The original asset
    # is identified by the `id` of the `CREATE` transaction that defined it.
    transfer_asset = {'id': bike_id}

    # Alice wants to spend the one and only output available, the one with index `0`.
    output_index = 0
    output = fulfilled_creation_tx['outputs'][output_index]

    # Here, she defines the `input` of the `TRANSFER` transaction. The `input` contains
    # several keys:
    #
    # - `fulfillment`, taken from the previous `CREATE` transaction.
    # - `fulfills`, that specifies which condition she is fulfilling.
    # - `owners_before`.
    transfer_input = {'fulfillment': output['condition']['details'],
                      'fulfills': {'output_index': output_index,
                                   'transaction_id': fulfilled_creation_tx['id']},
                      'owners_before': output['public_keys']}

    # Now that all the elements are set, she creates the actual transaction...
    prepared_transfer_tx = bdb.transactions.prepare(
            operation='TRANSFER',
            asset=transfer_asset,
            inputs=transfer_input,
            recipients=bob.public_key)

    # ... and signs it with her private key.
    fulfilled_transfer_tx = bdb.transactions.fulfill(
            prepared_transfer_tx,
            private_keys=alice.private_key)

    # She finally sends the transaction to a BigchainDB node.
    sent_transfer_tx = bdb.transactions.send_commit(fulfilled_transfer_tx)

    # And just to be 100% sure, she also checks if she can retrieve
    # it from the BigchainDB node.
    assert bdb.transactions.retrieve(fulfilled_transfer_tx['id']) == sent_transfer_tx

    # Now Alice has zero unspent transactions.
    assert len(bdb.outputs.get(alice.public_key, spent=False)) == 0

    # While Bob has one.
    assert len(bdb.outputs.get(bob.public_key, spent=False)) == 1

    # Bob double checks what he got was the actual bike.
    bob_tx_id = bdb.outputs.get(bob.public_key, spent=False)[0]['transaction_id']
    assert bdb.transactions.retrieve(bob_tx_id) == sent_transfer_tx
