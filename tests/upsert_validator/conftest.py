# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0
from unittest.mock import patch

import pytest

from bigchaindb.backend.localmongodb import query
from bigchaindb.upsert_validator import ValidatorElection


@pytest.fixture
def valid_upsert_validator_election_b(b, node_key, new_validator):
    voters = ValidatorElection.recipients(b)
    return ValidatorElection.generate([node_key.public_key],
                                      voters,
                                      new_validator, None).sign([node_key.private_key])


@pytest.fixture
@patch('bigchaindb.elections.election.uuid4', lambda: 'mock_uuid4')
def fixed_seed_election(b_mock, node_key, new_validator):
    voters = ValidatorElection.recipients(b_mock)
    return ValidatorElection.generate([node_key.public_key],
                                      voters,
                                      new_validator, None).sign([node_key.private_key])


@pytest.fixture
def concluded_election(b, ongoing_validator_election, ed25519_node_keys):
    query.store_election(b.connection, ongoing_validator_election.id,
                         2, is_concluded=True)
    return ongoing_validator_election


@pytest.fixture
def inconclusive_election(b, ongoing_validator_election, new_validator):
    validators = b.get_validators(height=1)
    validators[0]['voting_power'] = 15
    validator_update = {'validators': validators,
                        'height': 2,
                        'election_id': 'some_other_election'}

    query.store_validator_set(b.connection, validator_update)
    return ongoing_validator_election
