# Separate all crypto code so that we can easily test several implementations
from collections import namedtuple

import nacl.signing
import sha3
from cryptoconditions import crypto


CryptoKeypair = namedtuple('CryptoKeypair', ('private_key', 'public_key'))


def hash_data(data):
    """Hash the provided data using SHA3-256"""
    return sha3.sha3_256(data.encode()).hexdigest()

class Ed25519SigningKeyFromHash(crypto.Ed25519SigningKey):
    
    def __init__(self, key, encoding='base58'):
        super().__init__(key, encoding=encoding)

    @classmethod
    def generate(cls, hash_bytes):
        return cls(nacl.signing.SigningKey(hash_bytes).encode(encoder=crypto.Base58Encoder))


def ed25519_generate_key_pair_from_secret(secret):
    """ 
    Generate a new key pair. 
 
    Args: 
        secret (:class:`string`): A secret that serves as a seed 
 
    Returns: 
        A tuple of (private_key, public_key) encoded in base58. 
    """
    # if you want to do this correctly, use a key derivation function! 
    if not isinstance(secret, bytes): 
        secret = secret.encode() 
 
    hash_bytes = sha3.keccak_256(secret).digest() 
    sk = Ed25519SigningKeyFromHash.generate(hash_bytes=hash_bytes) 
    # Private key 
    private_value_base58 = sk.encode(encoding='base58') 
 
    # Public key 
    public_value_compressed_base58 = sk.get_verifying_key().encode(encoding='base58') 
 
    return private_value_base58, public_value_compressed_base58 


def generate_key_pair(secret=None):
    """Generates a cryptographic key pair.
    Args:
        secret (:class:`string`): A secret that serves as seed
    Returns:
        :class:`~bigchaindb.common.crypto.CryptoKeypair`: A
        :obj:`collections.namedtuple` with named fields
        :attr:`~bigchaindb.common.crypto.CryptoKeypair.private_key` and
        :attr:`~bigchaindb.common.crypto.CryptoKeypair.public_key`.

    """
    if secret:
        keypair_raw = ed25519_generate_key_pair_from_secret(secret)
    else:
        keypair_raw = crypto.ed25519_generate_key_pair()
    # TODO FOR CC: Adjust interface so that this function becomes unnecessary
    return CryptoKeypair(
        *(k.decode() for k in keypair_raw))


PrivateKey = crypto.Ed25519SigningKey
PublicKey = crypto.Ed25519VerifyingKey

