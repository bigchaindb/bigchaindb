import pytest

from bigchaindb.models import Transaction

pytestmark = [pytest.mark.tendermint, pytest.mark.bdb]


def test_upsert_validator_valid_election(validator_election, priv_validator_path,
                                         network_validators58, new_validator):

    # Create an election proposal to add a new validator
    tx_election = validator_election.propose(new_validator, priv_validator_path)

    voters = {}
    for output in tx_election.outputs:
        [output_public_key] = output.public_keys
        voters[output_public_key] = output.amount

    valid_asset = {
        'type': 'election',
        'name': 'upsert-validator',
        'version': '1.0',
        'args': new_validator
    }

    assert voters == network_validators58
    assert tx_election.asset['data'] == valid_asset
    assert validator_election.is_valid_proposal(tx_election)


def test_upsert_validator_invalid_election(b, validator_election, priv_validator_path,
                                           network_validators58, new_validator, node_keys58):
    from bigchaindb.tep.upsert_validator import load_node_key

    node_key = load_node_key(priv_validator_path)
    asset = validator_election._new_election_object(new_validator)
    recipients = validator_election._recipients()

    altered_recipients = []
    for r in recipients:
        ([r_public_key], voting_power) = r
        altered_recipients.append(([r_public_key], voting_power - 1))

    # Create a transaction which doesn't enfore the network power
    tx_election = Transaction.create([node_key.public_key],
                                     altered_recipients,
                                     asset=asset)\
                             .sign([node_key.private_key])

    assert not validator_election.is_valid_proposal(tx_election)

    # Assume that `tx_election` was valid election at the time of creation
    b.store_bulk_transactions([tx_election])
    votes = prepare_node_votes(node_keys58, validator_election, tx_election)
    configs = [[0], [1], [2], [3],
               [0, 1], [0, 2], [0, 3],
               [1, 2], [1, 3], [2, 3]]

    for vote_config in configs:
        curr_votes = []
        for index in vote_config:
            curr_votes.append(votes[index])

        (concluded, msg) = validator_election.get_election_status(tx_election.id, curr_votes)
        assert not concluded
        assert msg == 'inconsistent_topology'


def test_upsert_validator_valid_vote(b, validator_election, priv_validator_path,
                                     network_validators58, new_validator):

    tx_election = validator_election.propose(new_validator, priv_validator_path)
    b.store_bulk_transactions([tx_election])

    # Create vote for election_id
    tx_vote = validator_election.vote(tx_election.id, priv_validator_path)

    assert tx_vote.metadata == {'type': 'vote'}

    [tx_vote_input_public_key] = tx_vote.inputs[0].owners_before
    [tx_vote_ouput_public_key] = tx_vote.outputs[0].public_keys
    tx_voter_votes = tx_vote.outputs[0].amount

    election_id = validator_election.public_key(tx_election.id)

    # The vote should be casted to the election id
    assert tx_vote_ouput_public_key == election_id
    assert network_validators58[tx_vote_input_public_key] == tx_voter_votes
    assert validator_election.is_valid_vote(tx_vote)


def test_upsert_validator_conclude_election(b, validator_election, priv_validator_path,
                                            network_validators58, new_validator, node_keys58):

    tx_election = validator_election.propose(new_validator, priv_validator_path)
    b.store_bulk_transactions([tx_election])

    votes = prepare_node_votes(node_keys58, validator_election, tx_election)
    assert len(votes) == 4

    def assert_not_concluded(vote_configs):
        for vote_config in vote_configs:
            curr_votes = []
            for index in vote_config:
                curr_votes.append(votes[index])

            (concluded, msg) = validator_election.get_election_status(tx_election.id, curr_votes)
            assert not concluded
            assert msg == 'insufficient_votes'

    def assert_concluded(vote_configs):
        for vote_config in vote_configs:
            curr_votes = []
            for index in vote_config:
                curr_votes.append(votes[index])

            (concluded, msg) = validator_election.get_election_status(tx_election.id, curr_votes)
            assert concluded

    # Non concluding vote configs
    configs = [[0], [1], [2], [3],
               [0, 1], [0, 2], [0, 3],
               [1, 2], [1, 3], [2, 3]]
    assert_not_concluded(configs)

    configs = [[0, 1, 2], [0, 2, 3], [0, 1, 3], [1, 2, 3]]
    assert_concluded(configs)

    b.store_bulk_transactions([votes[0]])

    configs = [[1], [2], [3]]
    assert_not_concluded(configs)

    configs = [[1, 2], [1, 3], [2, 3]]
    assert_concluded(configs)

    b.store_bulk_transactions([votes[1]])

    configs = [[1], [2], [3]]
    assert_concluded(configs)


def test_upsert_validator_delegate_vote(b, validator_election, priv_validator_path,
                                        network_validators58, new_validator, node_keys58):
    from bigchaindb.common.crypto import generate_key_pair

    non_validator = generate_key_pair()

    tx_election = validator_election.propose(new_validator, priv_validator_path)
    b.store_bulk_transactions([tx_election])

    election_public_key = validator_election.public_key(tx_election.id)

    def delegate_vote(delegator_priv_key, delegatee_public_key, election_id,
                      tx_vote_input, voting_power):
        return Transaction.transfer(tx_vote_input,
                                    [([delegatee_public_key], voting_power)],
                                    asset_id=election_id)\
                          .sign([delegator_priv_key])

    def cast_delegated_vote(private_key, election_pk, tx_vote_input, voting_power):
        return Transaction.transfer(tx_vote_input,
                                    [([election_pk], voting_power)],
                                    metadata={'type': 'vote'},
                                    asset_id=tx_election.id)\
                          .sign([private_key])

    node0 = node_keys58[0]
    # node1 = node_keys58[1]

    (node0_tx_vote_input,
     node0_voting_power) = validator_election._get_vote(tx_election, node0.public_key)

    non_validator_dvote_node0 = delegate_vote(node0.private_key,
                                              non_validator.public_key,
                                              tx_election.id,
                                              node0_tx_vote_input,
                                              node0_voting_power)

    votes = prepare_node_votes(node_keys58[2:], validator_election, tx_election)

    assert validator_election.get_election_status(tx_election.id, votes) == (False, 'insufficient_votes')

    b.store_bulk_transactions([non_validator_dvote_node0])

    non_validator_vote = cast_delegated_vote(non_validator.private_key, election_public_key,
                                             non_validator_dvote_node0.to_inputs(),
                                             node0_voting_power)

    (concluded, msg) = validator_election.get_election_status(tx_election.id, votes)
    assert not concluded
    assert msg == 'insufficient_votes'

    (concluded, msg) = validator_election.get_election_status(tx_election.id, votes + [non_validator_vote])
    assert concluded

    b.store_bulk_transactions([non_validator_vote])

    (concluded, msg) = validator_election.get_election_status(tx_election.id, votes)
    assert concluded


def prepare_node_votes(node_keys58, validator_election, tx_election):
    votes = []
    election_id = validator_election.public_key(tx_election.id)
    for node_key in node_keys58:
        (tx_vote_input,
         voting_power) = validator_election._get_vote(tx_election, node_key.public_key)
        tx_vote = Transaction.transfer(tx_vote_input,
                                       [([election_id], voting_power)],
                                       metadata={'type': 'vote'},
                                       asset_id=tx_election.id)\
                             .sign([node_key.private_key])
        votes.append(tx_vote)
    return votes
