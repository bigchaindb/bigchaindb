import base64
import json


def encode_transaction(value):
    """Encode a transaction to Base64."""

    return base64.b64encode(json.dumps(value).encode('utf8')).decode('utf8')


def decode_transaction(raw):
    """Decode a transaction from Base64 to a dict."""

    return json.loads(raw.decode('utf8'))
