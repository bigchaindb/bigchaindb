# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

import pytest

from bigchaindb import ValidatorElectionVote
from bigchaindb.backend.localmongodb import query
from bigchaindb.lib import Block
from bigchaindb.upsert_validator import ValidatorElection


@pytest.fixture
def b_mock(b, network_validators):
    b.get_validators = mock_get_validators(network_validators)

    return b


def mock_get_validators(network_validators):
    def validator_set(height):
        validators = []
        for public_key, power in network_validators.items():
            validators.append({
                'public_key': {'type': 'ed25519-base64', 'value': public_key},
                'voting_power': power
            })
        return validators

    return validator_set


@pytest.fixture
def valid_election(b_mock, node_key, new_validator):
    voters = ValidatorElection.recipients(b_mock)
    return ValidatorElection.generate([node_key.public_key],
                                      voters,
                                      new_validator, None).sign([node_key.private_key])


@pytest.fixture
def valid_election_b(b, node_key, new_validator):
    voters = ValidatorElection.recipients(b)
    return ValidatorElection.generate([node_key.public_key],
                                      voters,
                                      new_validator, None).sign([node_key.private_key])


@pytest.fixture
def ongoing_election(b, valid_election, ed25519_node_keys):
    validators = b.get_validators(height=1)
    genesis_validators = {'validators': validators,
                          'height': 0,
                          'election_id': None}
    query.store_validator_set(b.connection, genesis_validators)

    b.store_bulk_transactions([valid_election])
    block_1 = Block(app_hash='hash_1', height=1, transactions=[valid_election.id])
    b.store_block(block_1._asdict())
    return valid_election


@pytest.fixture
def concluded_election(b, ongoing_election, ed25519_node_keys):
    validators = b.get_validators(height=1)
    validator_update = {'validators': validators,
                        'height': 2,
                        'election_id': ongoing_election.id}

    query.store_validator_set(b.connection, validator_update)
    return ongoing_election


@pytest.fixture
def inconclusive_election(b, ongoing_election, new_validator):
    validators = b.get_validators(height=1)
    validators[0]['voting_power'] = 15
    validator_update = {'validators': validators,
                        'height': 2,
                        'election_id': 'some_other_election'}

    query.store_validator_set(b.connection, validator_update)
    return ongoing_election


def vote(election, voter, keys, b):
    election_input = election.to_inputs()[voter]
    votes = election.outputs[voter].amount
    public_key = election_input.owners_before[0]
    key = keys[public_key]

    election_pub_key = ValidatorElection.to_public_key(election.id)

    v = ValidatorElectionVote.generate([election_input],
                                       [([election_pub_key], votes)],
                                       election_id=election.id)\
                             .sign([key.private_key])
    b.store_bulk_transactions([v])
    return v
