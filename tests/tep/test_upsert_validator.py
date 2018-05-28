import pytest
from unittest.mock import Mock


@pytest.mark.execute
@pytest.mark.tendermint
def test_upsert_validator_election(b, priv_validator_path, network_validators):
    from bigchaindb.tep.upsert_validator import UpsertValidator
    from bigchaindb.tendermint.lib import BigchainDB
    from bigchaindb.tendermint.utils import key_from_base64
    from bigchaindb.common.crypto import public_key_from_ed35519_key

    def mock_execute_action(tx):
        return tx

    def mock_get_validators():
        validators = []
        for public_key, power in network_validators.items():
            validators.append({
                'pub_key': {'type': 'AC26791624DE60', 'value': public_key},
                'voting_power': power
            })
        return validators

    def mock_write_transaction(tx):
        return (202, '')

    b_mock = BigchainDB()
    b_mock = Mock(spec=b_mock, write_transaction=mock_write_transaction,
                  get_validators=mock_get_validators)

    validator_election = UpsertValidator(bigchain=b_mock)
    validator_election._execute_action = mock_execute_action

    public_key = '1718D2DBFF00158A0852A17A01C78F4DCF3BA8E4FB7B8586807FAC182A535034'
    power = 1
    node_id = 'fake_node_id'

    validator = {'pub_key': public_key,
                 'power': power,
                 'node_id': node_id}

    tx_election = validator_election.propose(validator, priv_validator_path)

    validators = {}
    for validator_public_key, validator_power in network_validators.items():
        validator_public_key = public_key_from_ed35519_key(key_from_base64(validator_public_key))
        validators[validator_public_key] = validator_power

    voters = {}
    for output in tx_election.outputs:
        [output_public_key] = output.public_keys
        voters[output_public_key] = output.amount
        # assert network_validators[output.public_keys[0]] == output.amount

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
    assert validators == voters
    assert tx_election.asset['data'] == valid_asset
