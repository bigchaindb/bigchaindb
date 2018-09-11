# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

VALIDATORS_ENDPOINT = '/api/v1/validators/'


def test_get_validators_endpoint(b, client):
    validator_set = [{'address': 'F5426F0980E36E03044F74DD414248D29ABCBDB2',
                      'pub_key': {'data': '4E2685D9016126864733225BE00F005515200727FBAB1312FC78C8B76831255A',
                                  'type': 'ed25519'},
                      'voting_power': 10}]
    b.store_validator_set(23, validator_set)

    res = client.get(VALIDATORS_ENDPOINT)
    assert is_validator(res.json[0])
    assert res.status_code == 200


# Helper
def is_validator(v):
    return ('pub_key' in v) and ('voting_power' in v)
