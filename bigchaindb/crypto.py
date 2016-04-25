# Separate all crypto code so that we can easily test several implementations

import sha3
from cryptoconditions import ed25519


def hash_data(data):
    """Hash the provided data using SHA3-256"""
    return sha3.sha3_256(data.encode()).hexdigest()


def generate_key_pair():
    sk, pk = ed25519.ed25519_generate_key_pair()
    return sk.decode(), pk.decode()

SigningKey = ed25519.SigningKey
VerifyingKey = ed25519.VerifyingKey
