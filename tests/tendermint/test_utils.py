import base64
import json


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
