# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

import base64
import json

try:
    from hashlib import sha3_256
except ImportError:
    from sha3 import sha3_256


def test_encode_decode_transaction(b):
    from bigchaindb.tendermint_utils import (encode_transaction,
                                             decode_transaction)

    asset = {
        'value': 'key'
    }

    encode_tx = encode_transaction(asset)
    new_encode_tx = base64.b64encode(json.dumps(asset).
                                     encode('utf8')).decode('utf8')

    assert encode_tx == new_encode_tx

    de64 = base64.b64decode(encode_tx)
    assert asset == decode_transaction(de64)


def test_calculate_hash_no_key(b):
    from bigchaindb.tendermint_utils import calculate_hash

    # pass an empty list
    assert calculate_hash([]) == ''


# TODO test for the case of an empty list of hashes, and possibly other cases.
def test_merkleroot():
    from bigchaindb.tendermint_utils import merkleroot
    hashes = [sha3_256(i.encode()).digest() for i in 'abc']
    assert merkleroot(hashes) == (
        '78c7c394d3158c218916b7ae0ebdea502e0f4e85c08e3b371e3dfd824d389fa3')


SAMPLE_PUBLIC_KEY = {
    "address": "53DC09497A6ED73B342C78AB1E916076A03A8B95",
    "pub_key": {
        "type": "AC26791624DE60",
        "value": "7S+T/do70jvneAq0M1so2X3M1iWTSuwtuSAr3nVpfEw="
    }
}


def test_convert_base64_public_key_to_address():
    from bigchaindb.tendermint_utils import public_key64_to_address

    address = public_key64_to_address(SAMPLE_PUBLIC_KEY['pub_key']['value'])
    assert address == SAMPLE_PUBLIC_KEY['address']


def test_public_key_encoding_decoding():
    from bigchaindb.tendermint_utils import (public_key_from_base64,
                                             public_key_to_base64)

    public_key = public_key_from_base64(SAMPLE_PUBLIC_KEY['pub_key']['value'])
    base64_public_key = public_key_to_base64(public_key)

    assert base64_public_key == SAMPLE_PUBLIC_KEY['pub_key']['value']
