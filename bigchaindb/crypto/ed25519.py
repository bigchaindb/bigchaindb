# Separate all crypto code so that we can easily test several implementations

import base64

import base58
import ed25519

from bigchaindb.crypto.core import PrivateKey, PublicKey


class ED25519PrivateKey(PrivateKey):
    """
    PrivateKey instance
    """

    def __init__(self, key):
        """
        Instantiate the private key with the private_value encoded in base58
        """
        private_base64 = self.decode(key)
        self.private_key = self._private_key_from_private_base64(private_base64)

    def sign(self, data):
        """
        Sign data with private key
        """
        return self.private_key.sign(data.encode('utf-8'), encoding="base64")

    @staticmethod
    def encode(private_base64):
        """
        Encode the base64 number private_base64 to base58
        """
        return base58.b58encode(base64.b64decode(private_base64))

    @staticmethod
    def decode(key):
        """
        Decode the base58 private_value to base64
        """
        return base64.b64encode(base58.b58decode(key))

    @staticmethod
    def _private_key_from_private_base64(private_base64):
        """
        Return an instance of a ED25519 SignigKey from a base64 key
        """
        return ed25519.SigningKey(private_base64, encoding='base64')


class ED25519PublicKey(PublicKey):

    def __init__(self, key):
        """
        Instantiate the public key with the compressed public value encoded in base58
        """
        public_base64 = self.decode(key)
        self.public_key = self._public_key_from_public_base64(public_base64)

    def verify(self, data, signature, encoding='base64'):
        try:
            if encoding:
                data = data.encode('utf-8')
            self.public_key.verify(signature, data, encoding=encoding)
        except ed25519.BadSignatureError:
            return False

        return True

    @staticmethod
    def encode(public_base64):
        """
        Encode the public key represented by base64 to base58
        """
        return ED25519PrivateKey.encode(public_base64)

    @staticmethod
    def decode(public_value_compressed_base58):
        """
        Decode the base58 public_value to base64
        """
        return ED25519PrivateKey.decode(public_value_compressed_base58)

    def _public_key_from_public_base64(self, public_base64):
        """
        Return an instance of ED25519 VerifyingKey from a base64
        """
        return ed25519.VerifyingKey(public_base64, encoding='base64')


def ed25519_generate_key_pair():
    """
    Generate a new key pair and return the pair encoded in base58
    """
    sk, vk = ed25519.create_keypair()
    # Private key
    private_value_base58 = base58.b58encode(sk.to_bytes())

    # Public key
    public_value_compressed_base58 = base58.b58encode(vk.to_bytes())

    return (private_value_base58, public_value_compressed_base58)
