# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

import pytest

from bigchaindb.upsert_validator import ValidatorElection
from bigchaindb.common.exceptions import (DuplicateTransaction,
                                          UnequalValidatorSet,
                                          InvalidProposer,
                                          MultipleInputsError,
                                          InvalidPowerChange)

pytestmark = [pytest.mark.tendermint, pytest.mark.bdb]


def test_upsert_validator_valid_election(b_mock, new_validator, node_key):
    voters = ValidatorElection.recipients(b_mock)
    election = ValidatorElection.generate([node_key.public_key],
                                          voters,
                                          new_validator, None).sign([node_key.private_key])
    assert election.validate(b_mock)


def test_upsert_validator_invalid_power_election(b_mock, new_validator, node_key):
    voters = ValidatorElection.recipients(b_mock)
    new_validator['power'] = 30

    election = ValidatorElection.generate([node_key.public_key],
                                          voters,
                                          new_validator, None).sign([node_key.private_key])
    with pytest.raises(InvalidPowerChange):
        election.validate(b_mock)


def test_upsert_validator_invalid_proposed_election(b_mock, new_validator, node_key):
    from bigchaindb.common.crypto import generate_key_pair

    alice = generate_key_pair()
    voters = ValidatorElection.recipients(b_mock)
    election = ValidatorElection.generate([alice.public_key],
                                          voters,
                                          new_validator, None).sign([alice.private_key])
    with pytest.raises(InvalidProposer):
        election.validate(b_mock)


def test_upsert_validator_invalid_inputs_election(b_mock, new_validator, node_key):
    from bigchaindb.common.crypto import generate_key_pair

    alice = generate_key_pair()
    voters = ValidatorElection.recipients(b_mock)
    election = ValidatorElection.generate([node_key.public_key, alice.public_key],
                                          voters,
                                          new_validator, None).sign([node_key.private_key, alice.private_key])
    with pytest.raises(MultipleInputsError):
        election.validate(b_mock)


def test_upsert_validator_invalid_election(b_mock, new_validator, node_key):
    voters = ValidatorElection.recipients(b_mock)
    valid_election = ValidatorElection.generate([node_key.public_key],
                                                voters,
                                                new_validator, None).sign([node_key.private_key])
    duplicate_election = ValidatorElection.generate([node_key.public_key],
                                                    voters,
                                                    new_validator, None).sign([node_key.private_key])

    with pytest.raises(DuplicateTransaction):
        valid_election.validate(b_mock, [duplicate_election])

    b_mock.store_bulk_transactions([valid_election])

    with pytest.raises(DuplicateTransaction):
        duplicate_election.validate(b_mock)

    # Try creating an election with incomplete voter set
    invalid_election = ValidatorElection.generate([node_key.public_key],
                                                  voters[1:],
                                                  new_validator, None).sign([node_key.private_key])

    with pytest.raises(UnequalValidatorSet):
        invalid_election.validate(b_mock)

    recipients = ValidatorElection.recipients(b_mock)
    altered_recipients = []
    for r in recipients:
        ([r_public_key], voting_power) = r
        altered_recipients.append(([r_public_key], voting_power - 1))

    # Create a transaction which doesn't enfore the network power
    tx_election = ValidatorElection.generate([node_key.public_key],
                                             altered_recipients,
                                             new_validator, None).sign([node_key.private_key])

    with pytest.raises(UnequalValidatorSet):
        tx_election.validate(b_mock)
