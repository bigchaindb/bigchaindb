# Separate all crypto code so that we can easily test several implementations

import multihash
from cryptoconditions import crypto


def hash_data(data):
    """Hash the provided data using multihash SHA3-256"""
    return multihash.digest(data.encode(), 'sha3_256').encode('base58').decode('utf-8')


def generate_key_pair():
    sk, pk = crypto.ed25519_generate_key_pair()
    return sk.decode(), pk.decode()

SigningKey = crypto.Ed25519SigningKey
VerifyingKey = crypto.Ed25519VerifyingKey
