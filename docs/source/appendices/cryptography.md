# Cryptography

The section documents the cryptographic algorithms and Python implementations that we use.

Before hashing or computing the signature of a JSON document, we serialize it as described in [the section on JSON serialization](json-serialization.html).

## Hashes

BigchainDB's hashes are computed using [py-ipld](https://github.com/bigchaindb/py-ipld) (see: [IPLD specification](https://github.com/ipfs/specs/tree/master/ipld)). It uses [pymultihash](https://github.com/ivilata/pymultihash) (see: [multihash specification](https://github.com/jbenet/multihash)) to compute hashes with the SHA2-256 algorithm.
We store the base58-encoded hash in the database. For example:

```python
from ipld import marshal, multihash

data = "message"
tx_hash = marshal(multihash(data))
# => QmbLAJRGa3FupoH7tYdCdrWFEmCdwY7WHDX8zQskUtHndF
```

## Signature Algorithm and Keys

BigchainDB uses the [Ed25519](https://ed25519.cr.yp.to/) public-key signature system for generating its public/private key pairs (also called verifying/signing keys). Ed25519 is an instance of the [Edwards-curve Digital Signature Algorithm (EdDSA)](https://en.wikipedia.org/wiki/EdDSA). As of April 2016, EdDSA was in ["Internet-Draft" status with the IETF](https://tools.ietf.org/html/draft-irtf-cfrg-eddsa-05) but was [already widely used](https://ianix.com/pub/ed25519-deployment.html).

BigchainDB uses the the [ed25519](https://github.com/warner/python-ed25519) Python package, overloaded by the [cryptoconditions library](https://github.com/bigchaindb/cryptoconditions).

All keys are represented with the base58 encoding by default.
