import pytest

from bigchaindb.upsert_validator import ValidatorElectionVote
from bigchaindb.common.exceptions import AmountError


pytestmark = [pytest.mark.tendermint, pytest.mark.bdb]


def test_upsert_validator_valid_election_vote(b_mock, valid_election, ed25519_node_keys):
    b_mock.store_bulk_transactions([valid_election])

    input0 = valid_election.to_inputs()[0]
    votes = valid_election.outputs[0].amount
    public_key0 = input0.owners_before[0]
    key0 = ed25519_node_keys[public_key0]

    election_pub_key = ValidatorElectionVote.to_public_key(valid_election.id)

    vote = ValidatorElectionVote.generate([input0],
                                          [([election_pub_key], votes)],
                                          election_id=valid_election.id)\
                                .sign([key0.private_key])
    assert vote.validate(b_mock)


def test_upsert_validator_delegate_election_vote(b_mock, valid_election, ed25519_node_keys):
    from bigchaindb.common.crypto import generate_key_pair

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


def test_upsert_validator_invalid_election_vote(b_mock, valid_election, ed25519_node_keys):
    b_mock.store_bulk_transactions([valid_election])

    input0 = valid_election.to_inputs()[0]
    votes = valid_election.outputs[0].amount
    public_key0 = input0.owners_before[0]
    key0 = ed25519_node_keys[public_key0]

    election_pub_key = ValidatorElectionVote.to_public_key(valid_election.id)

    vote = ValidatorElectionVote.generate([input0],
                                          [([election_pub_key], votes+1)],
                                          election_id=valid_election.id)\
                                .sign([key0.private_key])

    with pytest.raises(AmountError):
        assert vote.validate(b_mock)
