# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

from functools import singledispatch

from bigchaindb.backend.localmongodb.connection import LocalMongoDBConnection
from bigchaindb.backend.schema import TABLES


@singledispatch
def flush_db(connection, dbname):
    raise NotImplementedError


@flush_db.register(LocalMongoDBConnection)
def flush_localmongo_db(connection, dbname):
    for t in TABLES:
        getattr(connection.conn[dbname], t).delete_many({})


def generate_block(bigchain):
    from bigchaindb.common.crypto import generate_key_pair
    from bigchaindb.models import Transaction
    import time

    alice = generate_key_pair()
    tx = Transaction.create([alice.public_key],
                            [([alice.public_key], 1)],
                            asset=None)\
                    .sign([alice.private_key])

    code, message = bigchain.write_transaction(tx, 'broadcast_tx_commit')
    assert code == 202
    time.sleep(2)
