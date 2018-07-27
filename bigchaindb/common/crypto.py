# Separate all crypto code so that we can easily test several implementations
from collections import namedtuple

import sha3
from cryptoconditions import crypto


CryptoKeypair = namedtuple('CryptoKeypair', ('private_key', 'public_key'))


def hash_data(data):
    """Hash the provided data using SHA3-256"""
    return sha3.sha3_256(data.encode()).hexdigest()


def generate_key_pair():
    """Generates a cryptographic key pair.

    Returns:
        :class:`~bigchaindb.common.crypto.CryptoKeypair`: A
        :obj:`collections.namedtuple` with named fields
        :attr:`~bigchaindb.common.crypto.CryptoKeypair.private_key` and
        :attr:`~bigchaindb.common.crypto.CryptoKeypair.public_key`.

    """
    # TODO FOR CC: Adjust interface so that this function becomes unnecessary
    return CryptoKeypair(
        *(k.decode() for k in crypto.ed25519_generate_key_pair()))


PrivateKey = crypto.Ed25519SigningKey
PublicKey = crypto.Ed25519VerifyingKey


def key_pair_from_ed25519_key(hex_private_key):
    """Generate base58 encode public-private key pair from a hex encoded private key"""
    priv_key = crypto.Ed25519SigningKey(bytes.fromhex(hex_private_key)[:32], encoding='bytes')
    public_key = priv_key.get_verifying_key()
    return CryptoKeypair(private_key=priv_key.encode(encoding='base58').decode('utf-8'),
                         public_key=public_key.encode(encoding='base58').decode('utf-8'))


def public_key_from_ed25519_key(hex_public_key):
    """Generate base58 public key from hex encoded public key"""
    public_key = crypto.Ed25519VerifyingKey(bytes.fromhex(hex_public_key), encoding='bytes')
    return public_key.encode(encoding='base58').decode('utf-8')
