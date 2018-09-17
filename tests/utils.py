# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

from functools import singledispatch

from bigchaindb import Vote
from bigchaindb.backend.localmongodb.connection import LocalMongoDBConnection
from bigchaindb.backend.schema import TABLES
from bigchaindb.elections.election import Election


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


def to_inputs(election, i, ed25519_node_keys):
    input0 = election.to_inputs()[i]
    votes = election.outputs[i].amount
    public_key0 = input0.owners_before[0]
    key0 = ed25519_node_keys[public_key0]
    return (input0, votes, key0)


def gen_vote(election, i, ed25519_node_keys):
    (input_i, votes_i, key_i) = to_inputs(election, i, ed25519_node_keys)
    election_pub_key = Election.to_public_key(election.id)
    return Vote.generate([input_i],
                         [([election_pub_key], votes_i)],
                         election_id=election.id)\
        .sign([key_i.private_key])
