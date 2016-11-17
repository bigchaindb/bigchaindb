# Separate all crypto code so that we can easily test several implementations

import sha3
from cryptoconditions import crypto


def hash_data(data):
    """Hash the provided data using SHA3-256"""
    return sha3.sha3_256(data.encode()).hexdigest()


def generate_key_pair():
    # TODO FOR CC: Adjust interface so that this function becomes unnecessary
    private_key, public_key = crypto.ed25519_generate_key_pair()
    return private_key.decode(), public_key.decode()


PrivateKey = crypto.Ed25519SigningKey
PublicKey = crypto.Ed25519VerifyingKey
