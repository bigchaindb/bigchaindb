# Cryptography

The section documents the cryptographic algorithms and Python implementations
that we use.

Before hashing or computing the signature of a JSON document, we serialize it
as described in [the section on JSON serialization](json-serialization.html).

## Hashes

BigchainDB computes transaction and block hashes using an implementation of the
[SHA3-256](https://pypi.python.org/pypi/pysha3)
algorithm provided by the
[**pysha3** package](https://bitbucket.org/tiran/pykeccak),
which is a wrapper around the optimized reference implementation
from [http://keccak.noekeon.org](http://keccak.noekeon.org).

**Important**: Since selecting the Keccak hashing algorithm for SHA-3 in 2012, NIST released a new version of the hash using the same algorithm but slightly different parameters. As of version 0.9, BigchainDB is using the latest version, supported by pysha3 1.0b1. See below for an example output of the hash function.

Here's the relevant code from `bigchaindb/bigchaindb/common/crypto.py:

```python
import sha3

def hash_data(data):
    """Hash the provided data using SHA3-256"""
    return sha3.sha3_256(data.encode()).hexdigest()
```

The incoming `data` is understood to be a Python 3 string,
which may contain Unicode characters such as `'ü'` or `'字'`.
The Python 3 `encode()` method converts `data` to a bytes object.
`sha3.sha3_256(data.encode())` is a _sha3.SHA3 object;
the `hexdigest()` method converts it to a hexadecimal string.
For example:

```python
>>> import sha3
>>> data = '字'
>>> sha3.sha3_256(data.encode()).hexdigest()
'2b38731ba4ef72d4034bef49e87c381d1fbe75435163b391dd33249331f91fe7'
>>> data = 'hello world'
>>> sha3.sha3_256(data.encode()).hexdigest()
'644bcc7e564373040999aac89e7622f3ca71fba1d972fd94a31c3bfbf24e3938'
```

Note: Hashlocks (which are one kind of crypto-condition)
may use a different hash function.


## Signature Algorithm and Keys

BigchainDB uses the [Ed25519](https://ed25519.cr.yp.to/) public-key signature
system for generating its public/private key pairs. Ed25519 is an instance of
the [Edwards-curve Digital Signature Algorithm
(EdDSA)](https://en.wikipedia.org/wiki/EdDSA). As of December 2016, EdDSA was an
["Internet-Draft" with the
IETF](https://tools.ietf.org/html/draft-irtf-cfrg-eddsa-08) but was [already
widely used](https://ianix.com/pub/ed25519-deployment.html).

BigchainDB uses the the 
[**cryptoconditions** package](https://github.com/bigchaindb/cryptoconditions)
to do signature and keypair-related calculations.
That package, in turn, uses the [**PyNaCl** package](https://pypi.python.org/pypi/PyNaCl),
a Python binding to the Networking and Cryptography (NaCl) library.

All keys are represented with
[a Base58 encoding](https://en.wikipedia.org/wiki/Base58).
The cryptoconditions package uses the
[**base58** package](https://pypi.python.org/pypi/base58)
to calculate a Base58 encoding.
(There's no standard for Base58 encoding.)
Here's an example public/private key pair:

```js
"keypair": {
    "public": "9WYFf8T65bv4S8jKU8wongKPD4AmMZAwvk1absFDbYLM",
    "private": "3x7MQpPq8AEUGEuzAxSVHjU1FhLWVQJKFNNkvHhJPGCX"
}
```
