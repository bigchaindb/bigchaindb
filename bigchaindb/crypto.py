# Separate all crypto code so that we can easily test several implementations

from ipld import marshal, multihash
from cryptoconditions import crypto


def hash_data(data):
    """Hash the provided data using IPLD-specific multihash SHA2-256"""
    marshalled_data = marshal(data)
    return multihash(marshalled_data)


def generate_key_pair():
    sk, pk = crypto.ed25519_generate_key_pair()
    return sk.decode(), pk.decode()

SigningKey = crypto.Ed25519SigningKey
VerifyingKey = crypto.Ed25519VerifyingKey
