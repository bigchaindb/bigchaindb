# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

import pytest
import codecs

import abci.types_pb2 as types


@pytest.fixture
def validator_pub_key():
    return 'B0E42D2589A455EAD339A035D6CE1C8C3E25863F268120AA0162AD7D003A4014'


@pytest.fixture
def init_chain_request():
    addr = codecs.decode(b'9FD479C869C7D7E7605BF99293457AA5D80C3033', 'hex')
    pk = codecs.decode(b'VAgFZtYw8bNR5TMZHFOBDWk9cAmEu3/c6JgRBmddbbI=',
                       'base64')
    val_a = types.Validator(address=addr, power=10,
                            pub_key=types.PubKey(type='ed25519', data=pk))

    return types.RequestInitChain(validators=[val_a])
