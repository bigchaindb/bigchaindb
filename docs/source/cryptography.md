# Cryptography

The section documents the cryptographic algorithms and Python implementations that we use.

The implementations that we have chosen for now are just for fast prototyping. Some of them are pure Python implementations which may be slow. As future work, we should look at other alternatives.

## Hashes

For hashing we are using the sha3-256 algorithm and [pysha3](https://bitbucket.org/tiran/pykeccak) as the Python implementation. We store the hex encoded hash in the database. For example:

```python
import hashlib
# monkey patch hashlib with sha3 functions
import sha3

data = "message"
tx_hash = hashlib.sha3_256(data).hexdigest()
```

## Keys

For signing and veryfing signatures we are using the ECDSA with 192bit key lengths and 
[python-ecdsa](https://github.com/warner/python-ecdsa) as the python implementation.

The public-key or verification key are converted to string and hex encoded before storing them to the blockchain. For example:

```python
import binascii
from ecdsa import SigningKey

# generate signing key in hex encoded form
sk = SigningKey.generate()
sk_hex = binascii.hexlify(sk.to_string())

# get signing key from hex
sk = SigningKey.from_string(binascii.unhexlify(sk_hex))
```
