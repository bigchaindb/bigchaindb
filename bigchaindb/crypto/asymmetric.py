# Separate all crypto code so that we can easily test several implementations
from abc import ABCMeta, abstractmethod

import sha3


class SigningKey(metaclass=ABCMeta):
    """
    PrivateKey instance
    """

    @abstractmethod
    def sign(self, data):
        """
        Sign data with private key

        Args:
            data:
        """

    @abstractmethod
    def get_verifying_key(self):
        """
        Get the associated verifying key

        Returns:
            A VerifyingKey object
        """

    @abstractmethod
    def to_ascii(self, prefix, encoding):
        """
        Encode the external value

        Args:
            prefix:
            encoding:
        """

    @staticmethod
    @abstractmethod
    def encode(private_value):
        """
        Encode the internal private_value to base58

        Args:
            private_value:
        """

    @staticmethod
    @abstractmethod
    def decode(private_base58):
        """
        Decode the base58 private value to internal value

        Args:
            private_base58 (base58):
        """
        raise NotImplementedError


class VerifyingKey(metaclass=ABCMeta):

    @abstractmethod
    def verify(self, data, signature):
        """
        Check the if the signature matches the data and this verifyingkey

        Args:
            data:
            signature:

        Returns:
            boolean:
        """

    @abstractmethod
    def to_ascii(self, prefix, encoding):
        """
        Encode the external value

        Args:
            prefix:
            encoding:
        """

    @staticmethod
    @abstractmethod
    def encode(public_value):
        """
        Encode the public key to base58 represented by the internal values

        Args:
            public_value
        """

    @staticmethod
    @abstractmethod
    def decode(public_base58):
        """
        Decode the base58 public_value to internal value

        Args:
            public_base58 (base58):
        """


def hash_data(data):
    """Hash the provided data using SHA3-256"""

    return sha3.sha3_256(data.encode()).hexdigest()


from bigchaindb.crypto.ecdsa import EcdsaSigningKey, EcdsaVerifyingKey, ecdsa_generate_key_pair

SigningKey = EcdsaSigningKey
VerifyingKey = EcdsaVerifyingKey
generate_key_pair = ecdsa_generate_key_pair
