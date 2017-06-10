def test_integration_web_api(bigchaindb_blackbox):
    import random
    import time

    from bigchaindb_driver import BigchainDB, exceptions
    from bigchaindb_driver.crypto import generate_keypair

    bdb = BigchainDB('http://localhost:9984')
    alice = generate_keypair()

    asset = {'data': {'random': random.random()}}
    tx = bdb.transactions.prepare(operation='CREATE',
                                  signers=alice.public_key,
                                  asset=asset)
    fftx = bdb.transactions.fulfill(tx, private_keys=alice.private_key)
    bdb.transactions.send(fftx)

    remote_tx = None

    for trial in range(10):
        try:
            remote_tx = bdb.transactions.retrieve(tx['id'])
        except exceptions.NotFoundError:
            time.sleep(1)
        else:
            break

    assert remote_tx['id'] == tx['id']
