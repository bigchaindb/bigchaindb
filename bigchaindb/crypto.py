# Separate all crypto code so that we can easily test several implementations

import sha3
from cryptoconditions import ecdsa, ed25519


signing_algorithm = 'ed25519'

if signing_algorithm == 'ecdsa':
    SigningKey = ecdsa.EcdsaSigningKey
    VerifyingKey = ecdsa.EcdsaVerifyingKey
    generate_key_pair = ecdsa.ecdsa_generate_key_pair

elif signing_algorithm == 'ed25519':
    SigningKey = ed25519.Ed25519SigningKey
    VerifyingKey = ed25519.Ed25519VerifyingKey
    generate_key_pair = ed25519.ed25519_generate_key_pair


def hash_data(data):
    """Hash the provided data using SHA3-256"""

    return sha3.sha3_256(data.encode()).hexdigest()


