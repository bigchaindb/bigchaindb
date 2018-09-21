# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

# # Divisible assets integration testing
# This test checks if we can successfully divide assets.
# The script tests various things like:
#
# - create a transaction with a divisible asset and issue them to someone
# - check if the transaction is stored and has the right amount of tokens
# - spend some tokens
# - try to spend more tokens than available
#
# We run a series of checks for each step, that is retrieving
# the transaction from the remote system, and also checking the `amount`
# of a given transaction.
#
# This integration test is a rip-off of our
# [tutorial](https://docs.bigchaindb.com/projects/py-driver/en/latest/usage.html).

# ## Imports
# We need some utils from the `os` package, we will interact with
# env variables.
# We need the `pytest` package to catch the `BadRequest` exception properly.
# And of course, we also need the `BadRequest`.
import os
import pytest
from bigchaindb_driver.exceptions import BadRequest

# For this test case we import and use the Python Driver.
from bigchaindb_driver import BigchainDB
from bigchaindb_driver.crypto import generate_keypair


def test_divisible_assets():
    # ## Set up a connection to BigchainDB
    # Check [test_basic.py](./test_basic.html) to get some more details
    # about the endpoint.
    bdb = BigchainDB(os.environ.get('BIGCHAINDB_ENDPOINT'))

    # Oh look, it is Alice again and she brought her friend Bob along.
    alice, bob = generate_keypair(), generate_keypair()

    # ## Alice creates a time sharing token
    # Alice wants to go on vacation, while Bobs bike just broke down.
    # Alice decides to rent her bike to Bob while she is gone.
    # So she prepares a `CREATE` transaction to issues 10 tokens.
    # First, she prepares an asset for a time sharing token. As you can see in
    # the description, Bob and Alice agree that each token can be used to ride
    # the bike for one hour.

    bike_token = {
        'data': {
            'token_for': {
                'bike': {
                    'serial_number': 420420
                }
            },
            'description': 'Time share token. Each token equals one hour of riding.',
        },
    }

    # She prepares a `CREATE` transaction and issues 10 tokens.
    # Here, Alice defines in a tuple that she wants to assign
    # these 10 tokens to Bob.
    prepared_token_tx = bdb.transactions.prepare(
        operation='CREATE',
        signers=alice.public_key,
        recipients=[([bob.public_key], 10)],
        asset=bike_token)

    # She fulfills and sends the transaction.
    fulfilled_token_tx = bdb.transactions.fulfill(
        prepared_token_tx,
        private_keys=alice.private_key)

    bdb.transactions.send_commit(fulfilled_token_tx)

    # We store the `id` of the transaction to use it later on.
    bike_token_id = fulfilled_token_tx['id']

    # Let's check if the transaction was successful.
    assert bdb.transactions.retrieve(bike_token_id), \
        'Cannot find transaction {}'.format(bike_token_id)

    # Bob owns 10 tokens now.
    assert bdb.transactions.retrieve(bike_token_id)['outputs'][0][
        'amount'] == '10'

    # ## Bob wants to use the bike
    # Now that Bob got the tokens and the sun is shining, he wants to get out
    # with the bike for three hours.
    # To use the bike he has to send the tokens back to Alice.
    # To learn about the details of transferring a transaction check out
    # [test_basic.py](./test_basic.html)
    transfer_asset = {'id': bike_token_id}

    output_index = 0
    output = fulfilled_token_tx['outputs'][output_index]
    transfer_input = {'fulfillment': output['condition']['details'],
                      'fulfills': {'output_index': output_index,
                                   'transaction_id': fulfilled_token_tx[
                                       'id']},
                      'owners_before': output['public_keys']}

    # To use the tokens Bob has to reassign 7 tokens to himself and the
    # amount he wants to use to Alice.
    prepared_transfer_tx = bdb.transactions.prepare(
        operation='TRANSFER',
        asset=transfer_asset,
        inputs=transfer_input,
        recipients=[([alice.public_key], 3), ([bob.public_key], 7)])

    # He signs and sends the transaction.
    fulfilled_transfer_tx = bdb.transactions.fulfill(
        prepared_transfer_tx,
        private_keys=bob.private_key)

    sent_transfer_tx = bdb.transactions.send_commit(fulfilled_transfer_tx)

    # First, Bob checks if the transaction was successful.
    assert bdb.transactions.retrieve(
        fulfilled_transfer_tx['id']) == sent_transfer_tx
    # There are two outputs in the transaction now.
    # The first output shows that Alice got back 3 tokens...
    assert bdb.transactions.retrieve(
        fulfilled_transfer_tx['id'])['outputs'][0]['amount'] == '3'

    # ... while Bob still has 7 left.
    assert bdb.transactions.retrieve(
        fulfilled_transfer_tx['id'])['outputs'][1]['amount'] == '7'

    # ## Bob wants to ride the bike again
    # It's been a week and Bob wants to right the bike again.
    # Now he wants to ride for 8 hours, that's a lot Bob!
    # He prepares the transaction again.

    transfer_asset = {'id': bike_token_id}
    # This time we need an `output_index` of 1, since we have two outputs
    # in the `fulfilled_transfer_tx` we created before. The first output with
    # index 0 is for Alice and the second output is for Bob.
    # Since Bob wants to spend more of his tokens he has to provide the
    # correct output with the correct amount of tokens.
    output_index = 1

    output = fulfilled_transfer_tx['outputs'][output_index]

    transfer_input = {'fulfillment': output['condition']['details'],
                      'fulfills': {'output_index': output_index,
                                   'transaction_id': fulfilled_transfer_tx['id']},
                      'owners_before': output['public_keys']}

    # This time Bob only provides Alice in the `recipients` because he wants
    # to spend all his tokens
    prepared_transfer_tx = bdb.transactions.prepare(
        operation='TRANSFER',
        asset=transfer_asset,
        inputs=transfer_input,
        recipients=[([alice.public_key], 8)])

    fulfilled_transfer_tx = bdb.transactions.fulfill(
        prepared_transfer_tx,
        private_keys=bob.private_key)

    # Oh Bob, what have you done?! You tried to spend more tokens than you had.
    # Remember Bob, last time you spent 3 tokens already,
    # so you only have 7 left.
    with pytest.raises(BadRequest) as error:
        bdb.transactions.send_commit(fulfilled_transfer_tx)

    # Now Bob gets an error saying that the amount he wanted to spent is
    # higher than the amount of tokens he has left.
    assert error.value.args[0] == 400
    message = 'Invalid transaction (AmountError): The amount used in the ' \
              'inputs `7` needs to be same as the amount used in the ' \
              'outputs `8`'
    assert error.value.args[2]['message'] == message

    # We have to stop this test now, I am sorry, but Bob is pretty upset
    # about his mistake. See you next time :)
