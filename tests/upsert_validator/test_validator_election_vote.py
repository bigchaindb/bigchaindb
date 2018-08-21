# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

import pytest
import codecs

from bigchaindb.tendermint_utils import public_key_to_base64
from bigchaindb.upsert_validator import ValidatorElection, ValidatorElectionVote
from bigchaindb.common.exceptions import AmountError
from bigchaindb.common.crypto import generate_key_pair
from bigchaindb.common.exceptions import ValidationError
from tests.utils import generate_block

pytestmark = [pytest.mark.execute]


@pytest.mark.tendermint
@pytest.mark.bdb
def test_upsert_validator_valid_election_vote(b_mock, valid_election, ed25519_node_keys):
    b_mock.store_bulk_transactions([valid_election])

    input0 = valid_election.to_inputs()[0]
    votes = valid_election.outputs[0].amount
    public_key0 = input0.owners_before[0]
    key0 = ed25519_node_keys[public_key0]

    election_pub_key = ValidatorElection.to_public_key(valid_election.id)

    vote = ValidatorElectionVote.generate([input0],
                                          [([election_pub_key], votes)],
                                          election_id=valid_election.id)\
                                .sign([key0.private_key])
    assert vote.validate(b_mock)


@pytest.mark.tendermint
@pytest.mark.bdb
def test_upsert_validator_valid_non_election_vote(b_mock, valid_election, ed25519_node_keys):
    b_mock.store_bulk_transactions([valid_election])

    input0 = valid_election.to_inputs()[0]
    votes = valid_election.outputs[0].amount
    public_key0 = input0.owners_before[0]
    key0 = ed25519_node_keys[public_key0]

    election_pub_key = ValidatorElection.to_public_key(valid_election.id)

    # Ensure that threshold conditions are now allowed
    with pytest.raises(ValidationError):
        ValidatorElectionVote.generate([input0],
                                       [([election_pub_key, key0.public_key], votes)],
                                       election_id=valid_election.id)\
                             .sign([key0.private_key])


@pytest.mark.tendermint
@pytest.mark.bdb
def test_upsert_validator_delegate_election_vote(b_mock, valid_election, ed25519_node_keys):
    alice = generate_key_pair()

    b_mock.store_bulk_transactions([valid_election])

    input0 = valid_election.to_inputs()[0]
    votes = valid_election.outputs[0].amount
    public_key0 = input0.owners_before[0]
    key0 = ed25519_node_keys[public_key0]

    delegate_vote = ValidatorElectionVote.generate([input0],
                                                   [([alice.public_key], 3), ([key0.public_key], votes-3)],
                                                   election_id=valid_election.id)\
                                         .sign([key0.private_key])

    assert delegate_vote.validate(b_mock)

    b_mock.store_bulk_transactions([delegate_vote])
    election_pub_key = ValidatorElection.to_public_key(valid_election.id)

    alice_votes = delegate_vote.to_inputs()[0]
    alice_casted_vote = ValidatorElectionVote.generate([alice_votes],
                                                       [([election_pub_key], 3)],
                                                       election_id=valid_election.id)\
                                             .sign([alice.private_key])
    assert alice_casted_vote.validate(b_mock)

    key0_votes = delegate_vote.to_inputs()[1]
    key0_casted_vote = ValidatorElectionVote.generate([key0_votes],
                                                      [([election_pub_key], votes-3)],
                                                      election_id=valid_election.id)\
                                            .sign([key0.private_key])
    assert key0_casted_vote.validate(b_mock)


@pytest.mark.tendermint
@pytest.mark.bdb
def test_upsert_validator_invalid_election_vote(b_mock, valid_election, ed25519_node_keys):
    b_mock.store_bulk_transactions([valid_election])

    input0 = valid_election.to_inputs()[0]
    votes = valid_election.outputs[0].amount
    public_key0 = input0.owners_before[0]
    key0 = ed25519_node_keys[public_key0]

    election_pub_key = ValidatorElection.to_public_key(valid_election.id)

    vote = ValidatorElectionVote.generate([input0],
                                          [([election_pub_key], votes+1)],
                                          election_id=valid_election.id)\
                                .sign([key0.private_key])

    with pytest.raises(AmountError):
        assert vote.validate(b_mock)


@pytest.mark.tendermint
@pytest.mark.bdb
def test_valid_election_votes_received(b_mock, valid_election, ed25519_node_keys):
    alice = generate_key_pair()
    b_mock.store_bulk_transactions([valid_election])
    assert valid_election.get_commited_votes(b_mock) == 0

    input0 = valid_election.to_inputs()[0]
    votes = valid_election.outputs[0].amount
    public_key0 = input0.owners_before[0]
    key0 = ed25519_node_keys[public_key0]

    # delegate some votes to alice
    delegate_vote = ValidatorElectionVote.generate([input0],
                                                   [([alice.public_key], 4), ([key0.public_key], votes-4)],
                                                   election_id=valid_election.id)\
                                         .sign([key0.private_key])
    b_mock.store_bulk_transactions([delegate_vote])
    assert valid_election.get_commited_votes(b_mock) == 0

    election_public_key = ValidatorElection.to_public_key(valid_election.id)
    alice_votes = delegate_vote.to_inputs()[0]
    key0_votes = delegate_vote.to_inputs()[1]

    alice_casted_vote = ValidatorElectionVote.generate([alice_votes],
                                                       [([election_public_key], 2), ([alice.public_key], 2)],
                                                       election_id=valid_election.id)\
                                             .sign([alice.private_key])

    assert alice_casted_vote.validate(b_mock)
    b_mock.store_bulk_transactions([alice_casted_vote])

    # Check if the delegated vote is count as valid vote
    assert valid_election.get_commited_votes(b_mock) == 2

    key0_casted_vote = ValidatorElectionVote.generate([key0_votes],
                                                      [([election_public_key], votes-4)],
                                                      election_id=valid_election.id)\
                                            .sign([key0.private_key])

    assert key0_casted_vote.validate(b_mock)
    b_mock.store_bulk_transactions([key0_casted_vote])

    assert valid_election.get_commited_votes(b_mock) == votes-2


@pytest.mark.tendermint
@pytest.mark.bdb
def test_valid_election_conclude(b_mock, valid_election, ed25519_node_keys):

    # Node 0: cast vote
    tx_vote0 = gen_vote(valid_election, 0, ed25519_node_keys)

    # check if the vote is valid even before the election doesn't exist
    with pytest.raises(ValidationError):
        assert tx_vote0.validate(b_mock)

    # store election
    b_mock.store_bulk_transactions([valid_election])
    # cannot conclude election as not votes exist
    assert not ValidatorElection.has_concluded(b_mock, valid_election.id)

    # validate vote
    assert tx_vote0.validate(b_mock)
    assert not ValidatorElection.has_concluded(b_mock, valid_election.id, [tx_vote0])

    b_mock.store_bulk_transactions([tx_vote0])
    assert not ValidatorElection.has_concluded(b_mock, valid_election.id)

    # Node 1: cast vote
    tx_vote1 = gen_vote(valid_election, 1, ed25519_node_keys)

    # Node 2: cast vote
    tx_vote2 = gen_vote(valid_election, 2, ed25519_node_keys)

    # Node 3: cast vote
    tx_vote3 = gen_vote(valid_election, 3, ed25519_node_keys)

    assert tx_vote1.validate(b_mock)
    assert not ValidatorElection.has_concluded(b_mock, valid_election.id, [tx_vote1])

    # 2/3 is achieved in the same block so the election can be.has_concludedd
    assert ValidatorElection.has_concluded(b_mock, valid_election.id, [tx_vote1, tx_vote2])

    b_mock.store_bulk_transactions([tx_vote1])
    assert not ValidatorElection.has_concluded(b_mock, valid_election.id)

    assert tx_vote2.validate(b_mock)
    assert tx_vote3.validate(b_mock)

    # conclusion can be triggered my different votes in the same block
    assert ValidatorElection.has_concluded(b_mock, valid_election.id, [tx_vote2])
    assert ValidatorElection.has_concluded(b_mock, valid_election.id, [tx_vote2, tx_vote3])

    b_mock.store_bulk_transactions([tx_vote2])

    # Once the blockchain records >2/3 of the votes the election is assumed to be.has_concludedd
    # so any invocation of `.has_concluded` for that election should return False
    assert not ValidatorElection.has_concluded(b_mock, valid_election.id)

    # Vote is still valid but the election cannot be.has_concludedd as it it assmed that it has
    # been.has_concludedd before
    assert tx_vote3.validate(b_mock)
    assert not ValidatorElection.has_concluded(b_mock, valid_election.id, [tx_vote3])


@pytest.mark.abci
def test_upsert_validator(b, node_key, node_keys, ed25519_node_keys):
    import time
    import requests

    if b.get_latest_block()['height'] == 0:
        generate_block(b)

    (node_pub, _) = list(node_keys.items())[0]

    validators = [{'pub_key': {'type': 'ed25519',
                               'data': node_pub},
                   'voting_power': 10}]

    latest_block = b.get_latest_block()
    # reset the validator set
    b.store_validator_set(latest_block['height'], validators)

    power = 1
    public_key = '9B3119650DF82B9A5D8A12E38953EA47475C09F0C48A4E6A0ECE182944B24403'
    public_key64 = public_key_to_base64(public_key)
    new_validator = {'public_key': public_key,
                     'node_id': 'some_node_id',
                     'power': power}

    voters = ValidatorElection.recipients(b)
    election = ValidatorElection.generate([node_key.public_key],
                                          voters,
                                          new_validator, None).sign([node_key.private_key])
    code, message = b.write_transaction(election, 'broadcast_tx_commit')
    assert code == 202
    time.sleep(3)

    assert b.get_transaction(election.id)

    tx_vote = gen_vote(election, 0, ed25519_node_keys)
    assert tx_vote.validate(b)
    code, message = b.write_transaction(tx_vote, 'broadcast_tx_commit')
    assert code == 202
    time.sleep(3)

    resp = requests.get(b.endpoint + 'validators')
    validator_pub_keys = []
    for v in resp.json()['result']['validators']:
        validator_pub_keys.append(v['pub_key']['value'])

    assert (public_key64 in validator_pub_keys)
    new_validator_set = b.get_validators()
    validator_pub_keys = []
    for v in new_validator_set:
        validator_pub_keys.append(v['pub_key']['data'])

    assert (public_key64 in validator_pub_keys)


@pytest.mark.tendermint
@pytest.mark.bdb
def test_get_validator_update(b, node_keys, node_key, ed25519_node_keys):
    reset_validator_set(b, node_keys, 1)

    power = 1
    public_key = '9B3119650DF82B9A5D8A12E38953EA47475C09F0C48A4E6A0ECE182944B24403'
    public_key64 = public_key_to_base64(public_key)
    new_validator = {'public_key': public_key,
                     'node_id': 'some_node_id',
                     'power': power}
    voters = ValidatorElection.recipients(b)
    election = ValidatorElection.generate([node_key.public_key],
                                          voters,
                                          new_validator).sign([node_key.private_key])
    # store election
    b.store_bulk_transactions([election])

    tx_vote0 = gen_vote(election, 0, ed25519_node_keys)
    tx_vote1 = gen_vote(election, 1, ed25519_node_keys)
    tx_vote2 = gen_vote(election, 2, ed25519_node_keys)

    assert not ValidatorElection.has_concluded(b, election.id, [tx_vote0])
    assert not ValidatorElection.has_concluded(b, election.id, [tx_vote0, tx_vote1])
    assert ValidatorElection.has_concluded(b, election.id, [tx_vote0, tx_vote1, tx_vote2])

    assert ValidatorElection.get_validator_update(b, 4, [tx_vote0]) == []
    assert ValidatorElection.get_validator_update(b, 4, [tx_vote0, tx_vote1]) == []

    update = ValidatorElection.get_validator_update(b, 4, [tx_vote0, tx_vote1, tx_vote2])
    update_public_key = codecs.encode(update[0].pub_key.data, 'base64').decode().rstrip('\n')
    assert len(update) == 1
    assert update_public_key == public_key64

    b.store_bulk_transactions([tx_vote0, tx_vote1])

    update = ValidatorElection.get_validator_update(b, 4, [tx_vote2])
    print('update', update)
    update_public_key = codecs.encode(update[0].pub_key.data, 'base64').decode().rstrip('\n')
    assert len(update) == 1
    assert update_public_key == public_key64


# ============================================================================
# Helper functions
# ============================================================================
def to_inputs(election, i, ed25519_node_keys):
    input0 = election.to_inputs()[i]
    votes = election.outputs[i].amount
    public_key0 = input0.owners_before[0]
    key0 = ed25519_node_keys[public_key0]
    return (input0, votes, key0)


def gen_vote(election, i, ed25519_node_keys):
    (input_i, votes_i, key_i) = to_inputs(election, i, ed25519_node_keys)
    election_pub_key = ValidatorElection.to_public_key(election.id)
    return ValidatorElectionVote.generate([input_i],
                                          [([election_pub_key], votes_i)],
                                          election_id=election.id)\
                                .sign([key_i.private_key])


def reset_validator_set(b, node_keys, height):
    validators = []
    for (node_pub, _) in node_keys.items():
        validators.append({'pub_key': {'type': 'ed25519',
                                       'data': node_pub},
                           'voting_power': 10})
    b.store_validator_set(height, validators)
