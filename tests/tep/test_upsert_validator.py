import pytest

from bigchaindb.models import Transaction


@pytest.mark.tendermint
def test_upsert_validator_valid_election(validator_election, priv_validator_path, network_validators58):
    public_key = '1718D2DBFF00158A0852A17A01C78F4DCF3BA8E4FB7B8586807FAC182A535034'
    power = 1
    node_id = 'fake_node_id'

    validator = {'pub_key': public_key,
                 'power': power,
                 'node_id': node_id}

    # Create an election proposal to add a new validator
    tx_election = validator_election.propose(validator, priv_validator_path)

    voters = {}
    for output in tx_election.outputs:
        [output_public_key] = output.public_keys
        voters[output_public_key] = output.amount

    valid_asset = {
        'type': 'election',
        'name': 'upsert-validator',
        'version': '1.0',
        'args': {
            'public_key': public_key,
            'power': power,
            'node_id': node_id
        }
    }

    assert voters == network_validators58
    assert tx_election.asset['data'] == valid_asset
    assert validator_election.is_valid_proposal(tx_election)


@pytest.mark.tendermint
def test_upsert_validator_invalid_election(validator_election, priv_validator_path, network_validators58):
    from bigchaindb.tep.upsert_validator import load_node_key

    public_key = '1718D2DBFF00158A0852A17A01C78F4DCF3BA8E4FB7B8586807FAC182A535034'
    power = 1
    node_id = 'fake_node_id'

    validator = {'pub_key': public_key,
                 'power': power,
                 'node_id': node_id}

    node_key = load_node_key(priv_validator_path)
    asset = validator_election._new_election_object(validator)
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
