# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

# # Stream Acceptance Test
# This test checks if the event stream works correctly. The basic idea of this
# test is to generate some random **valid** transaction, send them to a
# BigchainDB node, and expect those transactions to be returned by the valid
# transactions Stream API. During this test, two threads work together,
# sharing a queue to exchange events.
#
# - The *main thread* first creates and sends the transactions to BigchainDB;
# then it run through all events in the shared queue to check if all
# transactions sent have been validated by BigchainDB.
# - The *listen thread* listens to the events coming from BigchainDB and puts
# them in a queue shared with the main thread.

import os
import queue
import json
from threading import Thread, Event
from uuid import uuid4

# For this script, we need to set up a websocket connection, that's the reason
# we import the
# [websocket](https://github.com/websocket-client/websocket-client) module
from websocket import create_connection

from bigchaindb_driver import BigchainDB
from bigchaindb_driver.crypto import generate_keypair


def test_stream():
    # ## Set up the test
    # We use the env variable `BICHAINDB_ENDPOINT` to know where to connect.
    # Check [test_basic.py](./test_basic.html) for more information.
    BDB_ENDPOINT = os.environ.get('BIGCHAINDB_ENDPOINT')

    # *That's pretty bad, but let's do like this for now.*
    WS_ENDPOINT = 'ws://{}:9985/api/v1/streams/valid_transactions'.format(BDB_ENDPOINT.rsplit(':')[0])

    bdb = BigchainDB(BDB_ENDPOINT)

    # Hello to Alice again, she is pretty active in those tests, good job
    # Alice!
    alice = generate_keypair()

    # We need few variables to keep the state, specifically we need `sent` to
    # keep track of all transactions Alice sent to BigchainDB, while `received`
    # are the transactions BigchainDB validated and sent back to her.
    sent = []
    received = queue.Queue()

    # In this test we use a websocket. The websocket must be started **before**
    # sending transactions to BigchainDB, otherwise we might lose some
    # transactions. The `ws_ready` event is used to synchronize the main thread
    # with the listen thread.
    ws_ready = Event()

    # ## Listening to events
    # This is the function run by the complementary thread.
    def listen():
        # First we connect to the remote endpoint using the WebSocket protocol.
        ws = create_connection(WS_ENDPOINT)

        # After the connection has been set up, we can signal the main thread
        # to proceed (continue reading, it should make sense in a second.)
        ws_ready.set()

        # It's time to consume all events coming from the BigchainDB stream API.
        # Every time a new event is received, it is put in the queue shared
        # with the main thread.
        while True:
            result = ws.recv()
            received.put(result)

    # Put `listen` in a thread, and start it. Note that `listen` is a local
    # function and it can access all variables in the enclosing function.
    t = Thread(target=listen, daemon=True)
    t.start()

    # ## Pushing the transactions to BigchainDB
    # After starting the listen thread, we wait for it to connect, and then we
    # proceed.
    ws_ready.wait()

    # Here we prepare, sign, and send ten different `CREATE` transactions. To
    # make sure each transaction is different from the other, we generate a
    # random `uuid`.
    for _ in range(10):
        tx = bdb.transactions.fulfill(
                bdb.transactions.prepare(
                    operation='CREATE',
                    signers=alice.public_key,
                    asset={'data': {'uuid': str(uuid4())}}),
                private_keys=alice.private_key)
        # We don't want to wait for each transaction to be in a block. By using
        # `async` mode, we make sure that the driver returns as soon as the
        # transaction is pushed to the BigchainDB API. Remember: we expect all
        # transactions to be in the shared queue: this is a two phase test,
        # first we send a bunch of transactions, then we check if they are
        # valid (and, in this case, they should).
        bdb.transactions.send_async(tx)

        # The `id` of every sent transaction is then stored in a list.
        sent.append(tx['id'])

    # ## Check the valid transactions coming from BigchainDB
    # Now we are ready to check if BigchainDB did its job. A simple way to
    # check if all sent transactions have been processed is to **remove** from
    # `sent` the transactions we get from the *listen thread*. At one point in
    # time, `sent` should be empty, and we exit the test.
    while sent:
        # To avoid waiting forever, we have an arbitrary timeout of 5
        # seconds: it should be enough time for BigchainDB to create
        # blocks, in fact a new block is created every second. If we hit
        # the timeout, then game over ¯\\\_(ツ)\_/¯
        try:
            event = received.get(timeout=5)
            txid = json.loads(event)['transaction_id']
        except queue.Empty:
            assert False, 'Did not receive all expected transactions'

        # Last thing is to try to remove the `txid` from the set of sent
        # transactions. If this test is running in parallel with others, we
        # might get a transaction id of another test, and `remove` can fail.
        # It's OK if this happens.
        try:
            sent.remove(txid)
        except ValueError:
            pass
