# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

import base58
import base64
import random

from functools import singledispatch

from bigchaindb.backend.localmongodb.connection import LocalMongoDBConnection
from bigchaindb.backend.schema import TABLES
from bigchaindb.common import crypto
from bigchaindb.common.transaction_mode_types import BROADCAST_TX_COMMIT
from bigchaindb.elections.election import Election, Vote
from bigchaindb.tendermint_utils import key_to_base64


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

    alice = generate_key_pair()
    tx = Transaction.create([alice.public_key],
                            [([alice.public_key], 1)],
                            asset=None)\
                    .sign([alice.private_key])

    code, message = bigchain.write_transaction(tx, BROADCAST_TX_COMMIT)
    assert code == 202


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


def generate_validators(powers):
    """Generates an arbitrary number of validators with random public keys.

       The object under the `storage` key is in the format expected by DB.

       The object under the `eleciton` key is in the format expected by
       the upsert validator election.

       `public_key`, `private_key` are in the format used for signing transactions.

       Args:
           powers: A list of intergers representing the voting power to
                   assign to the corresponding validators.
    """
    validators = []
    for power in powers:
        kp = crypto.generate_key_pair()
        validators.append({
            'storage': {
                'public_key': {
                    'value': key_to_base64(base58.b58decode(kp.public_key).hex()),
                    'type': 'ed25519-base64',
                },
                'voting_power': power,
            },
            'election': {
                'node_id': f'node-{random.choice(range(100))}',
                'power': power,
                'public_key': {
                    'value': base64.b16encode(base58.b58decode(kp.public_key)).decode('utf-8'),
                    'type': 'ed25519-base16',
                },
            },
            'public_key': kp.public_key,
            'private_key': kp.private_key,
        })
    return validators


def generate_election(b, cls, public_key, private_key, asset_data, voter_keys):
    voters = cls.recipients(b)
    election = cls.generate([public_key],
                            voters,
                            asset_data,
                            None).sign([private_key])

    votes = [Vote.generate([election.to_inputs()[i]],
                           [([Election.to_public_key(election.id)], power)],
                           election.id) for i, (_, power) in enumerate(voters)]
    for key, v in zip(voter_keys, votes):
        v.sign([key])

    return election, votes
