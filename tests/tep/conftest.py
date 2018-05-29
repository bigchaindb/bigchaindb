import pytest
from bigchaindb.tep.upsert_validator import UpsertValidator


@pytest.fixture
def b_mock(b, network_validators):
    b.write_transaction = mock_write_transaction
    b.get_validators = mock_get_validators(network_validators)

    return b


@pytest.fixture
def validator_election(b_mock):
    validator_election = UpsertValidator(bigchain=b_mock)
    validator_election._execute_action = mock_execute_action

    return validator_election


def mock_execute_action(tx):
    return tx


def mock_write_transaction(tx):
    return (202, '')


def mock_get_validators(network_validators):
    def validator_set():
        validators = []
        for public_key, power in network_validators.items():
            validators.append({
                'pub_key': {'type': 'AC26791624DE60', 'value': public_key},
                'voting_power': power
            })
        return validators

    return validator_set
