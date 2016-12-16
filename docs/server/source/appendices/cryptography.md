# Cryptography

The section documents the cryptographic algorithms and Python implementations
that we use.

Before hashing or computing the signature of a JSON document, we serialize it
as described in [the section on JSON serialization](json-serialization.html).

## Hashes

BigchainDB computes transaction and block hashes using an implementation of the
[SHA3-256](https://en.wikipedia.org/wiki/SHA-3)
algorithm provided by the
[**pysha3** package](https://bitbucket.org/tiran/pykeccak),
which is a wrapper around the optimized reference implementation
from [http://keccak.noekeon.org](http://keccak.noekeon.org).

Here's the relevant code from `bigchaindb/bigchaindb/common/crypto.py`
(as of 11 December 2016):

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
'c67820de36d949a35ca24492e15767e2972b22f77213f6704ac0adec123c5690'
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
