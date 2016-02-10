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

## Signature algorithm and keys

The signature algorithm used by BigchainDB is ECDSA with the secp256k1 curve
using the python [cryptography](https://cryptography.io/en/latest/) module.

The private key is the base58 encoded hexadecimal representation of private number.
The public key is the base58 encoded hexadecimal representation of the
compressed public numbers.
