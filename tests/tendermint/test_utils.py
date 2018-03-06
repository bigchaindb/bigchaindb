import base64
import json

try:
    from hashlib import sha3_256
except ImportError:
    from sha3 import sha3_256

import pytest

pytestmark = pytest.mark.tendermint


def test_encode_decode_transaction(b):
    from bigchaindb.tendermint.utils import (encode_transaction,
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
    from bigchaindb.tendermint.utils import calculate_hash

    # pass an empty list
    assert calculate_hash([]) == ''


# TODO test for the case of an empty list of hashes, and possibly other cases.
def test_merkleroot():
    from bigchaindb.tendermint.utils import merkleroot
    hashes = [sha3_256(i.encode()).digest() for i in 'abc']
    assert merkleroot(hashes) == (
        '78c7c394d3158c218916b7ae0ebdea502e0f4e85c08e3b371e3dfd824d389fa3')
