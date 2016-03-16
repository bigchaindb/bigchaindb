# Separate all crypto code so that we can easily test several implementations
from abc import ABCMeta, abstractmethod

import sha3


class PrivateKey(metaclass=ABCMeta):
    """
    PrivateKey instance
    """

    @abstractmethod
    def sign(self, data):
        """
        Sign data with private key
        """
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def encode(private_value):
        """
        Encode the decimal number private_value to base58
        """
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def decode(key):
        """
        Decode the base58 private_value to decimale
        """
        raise NotImplementedError


class PublicKey(metaclass=ABCMeta):

    @abstractmethod
    def verify(self, data, signature):
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def encode(public_value_x, public_value_y):
        """
        Encode the public key represented by the decimal values x and y to base58
        """
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def decode(public_value_compressed_base58):
        """
        Decode the base58 public_value to the decimal x and y values
        """
        raise NotImplementedError


def hash_data(data):
    """Hash the provided data using SHA3-256"""

    return sha3.sha3_256(data.encode()).hexdigest()


from bigchaindb.crypto.ecdsa import ECDSAPrivateKey, ECDSAPublicKey, ecdsa_generate_key_pair

PrivateKey = ECDSAPrivateKey
PublicKey = ECDSAPublicKey
generate_key_pair = ecdsa_generate_key_pair
