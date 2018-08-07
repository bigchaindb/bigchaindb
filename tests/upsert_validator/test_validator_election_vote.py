import pytest

from bigchaindb.upsert_validator import ValidatorElection, ValidatorElectionVote
from bigchaindb.common.exceptions import AmountError
from bigchaindb.common.crypto import generate_key_pair
from bigchaindb.common.exceptions import ValidationError


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
    assert not ValidatorElection.conclude(b_mock, valid_election.id)

    # validate vote
    assert tx_vote0.validate(b_mock)
    assert not ValidatorElection.conclude(b_mock, valid_election.id, [tx_vote0])

    b_mock.store_bulk_transactions([tx_vote0])
    assert not ValidatorElection.conclude(b_mock, valid_election.id)

    # Node 1: cast vote
    tx_vote1 = gen_vote(valid_election, 1, ed25519_node_keys)

    # Node 2: cast vote
    tx_vote2 = gen_vote(valid_election, 2, ed25519_node_keys)

    # Node 3: cast vote
    tx_vote3 = gen_vote(valid_election, 3, ed25519_node_keys)

    assert tx_vote1.validate(b_mock)
    assert not ValidatorElection.conclude(b_mock, valid_election.id, [tx_vote1])

    # 2/3 is achieved in the same block so the election can be concluded
    assert ValidatorElection.conclude(b_mock, valid_election.id, [tx_vote1, tx_vote2])

    b_mock.store_bulk_transactions([tx_vote1])
    assert not ValidatorElection.conclude(b_mock, valid_election.id)

    assert tx_vote2.validate(b_mock)
    assert tx_vote3.validate(b_mock)

    # conclusion can be triggered my different votes in the same block
    assert ValidatorElection.conclude(b_mock, valid_election.id, [tx_vote2])
    assert ValidatorElection.conclude(b_mock, valid_election.id, [tx_vote2, tx_vote3])

    b_mock.store_bulk_transactions([tx_vote2])

    # Once the blockchain records >2/3 of the votes the election is assumed to be concluded
    # so any invocation of `.conclude` for that election should return False
    assert not ValidatorElection.conclude(b_mock, valid_election.id)

    # Vote is still valid but the election cannot be concluded as it it assmed that it has
    # been concluded before
    assert tx_vote3.validate(b_mock)
    assert not ValidatorElection.conclude(b_mock, valid_election.id, [tx_vote3])


@pytest.mark.tendermint
@pytest.mark.bdb
def test_get_validator_update(b_mock, valid_election, ed25519_node_keys):
    # store election
    b_mock.store_bulk_transactions([valid_election])

    # Node 0: cast vote
    tx_vote0 = gen_vote(valid_election, 0, ed25519_node_keys)
    assert b_mock.get_validator_update([tx_vote0]) == []
    b_mock.store_bulk_transactions([tx_vote0])

    tx_vote1 = gen_vote(valid_election, 1, ed25519_node_keys)
    assert b_mock.get_validator_update([tx_vote1]) == []
    b_mock.store_bulk_transactions([tx_vote1])

    # Election can only be concluded once
    tx_vote2 = gen_vote(valid_election, 2, ed25519_node_keys)
    assert b_mock.get_validator_update([tx_vote2]) == [valid_election.asset['data']]
    b_mock.store_bulk_transactions([tx_vote2])

    tx_vote3 = gen_vote(valid_election, 3, ed25519_node_keys)
    assert b_mock.get_validator_update([tx_vote3]) == []


@pytest.mark.abci
def test_upsert_validator(b, node_key, node_keys, new_validator, ed25519_node_keys):
    from bigchaindb.backend import connect
    from bigchaindb.tendermint_utils import public_key_to_base64
    import time
    import requests

    conn = connect()
    (node_pub, _) = list(node_keys.items())[0]

    validators = [{'address': 'some_address',
                   'pub_key': {'type': 'ed25519',
                               'data': node_pub},
                   'voting_power': 10}]

    # reset the validator set
    conn.run(
        conn.collection('validators').find_one_and_update(
            {"height": 1},
            {"$set": {"validators": validators}}
        )
    )

    power = 1
    public_key = '9B3119650DF82B9A5D8A12E38953EA47475C09F0C48A4E6A0ECE182944B24403'
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

    assert (public_key_to_base64(public_key) in validator_pub_keys)


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
