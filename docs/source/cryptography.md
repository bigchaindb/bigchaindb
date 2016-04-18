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

## Signature Algorithm and Keys

BigchainDB uses the [Ed25519](https://ed25519.cr.yp.to/) public-key signature system for generating its public/private key pairs (also called verifying/signing keys). Ed25519 is an instance of the [Edwards-curve Digital Signature Algorithm (EdDSA)](https://en.wikipedia.org/wiki/EdDSA). As of April 2016, EdDSA was in ["Internet-Draft" status with the IETF](https://tools.ietf.org/html/draft-irtf-cfrg-eddsa-05) but was [already widely used](https://ianix.com/pub/ed25519-deployment.html).

BigchainDB uses the the [ed25519](https://github.com/warner/python-ed25519) Python package, overloaded by the [cryptoconditions library](https://github.com/bigchaindb/cryptoconditions).

All keys are represented with the base58 encoding by default.