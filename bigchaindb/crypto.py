# Separate all crypto code so that we can easily test several implementations

from cryptoconditions import crypto
from ipld import multihash


def hash_data(serialized_data):
    """Hash the provided data using IPLD-specific multihash SHA2-256"""
    return multihash(serialized_data)


def generate_key_pair():
    sk, pk = crypto.ed25519_generate_key_pair()
    return sk.decode(), pk.decode()

SigningKey = crypto.Ed25519SigningKey
VerifyingKey = crypto.Ed25519VerifyingKey
