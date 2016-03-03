# Separate all crypto code so that we can easily test several implementations

import binascii
import base58

import sha3
import bitcoin

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from cryptography.exceptions import InvalidSignature


class PrivateKey(object):
    """
    PrivateKey instance
    """

    def __init__(self, key):
        """
        Instantiate the private key with the private_value encoded in base58
        """
        private_value = self.decode(key)
        private_numbers = self._private_value_to_cryptography_private_numbers(private_value)
        self.private_key = self._cryptography_private_key_from_private_numbers(private_numbers)

    def sign(self, data):
        """
        Sign data with private key
        """
        signer = self.private_key.signer(ec.ECDSA(hashes.SHA256()))
        signer.update(data.encode('utf-8'))
        signature = signer.finalize()
        return binascii.hexlify(signature).decode('utf-8')


    @staticmethod
    def encode(private_value):
        """
        Encode the decimal number private_value to base58
        """
        private_value_hex = bitcoin.encode_privkey(private_value, 'hex')
        private_value_base58 = base58.b58encode(bytes.fromhex(private_value_hex))
        return private_value_base58

    @staticmethod
    def decode(key):
        """
        Decode the base58 private_value to decimale
        """
        private_value_hex = binascii.hexlify(base58.b58decode(key))
        private_value = bitcoin.decode_privkey(private_value_hex)
        return private_value

    def _private_value_to_public_values(self, private_value):
        """
        Return the public values from the private value
        """
        public_value_x, public_value_y = bitcoin.privkey_to_pubkey(private_value)
        return (public_value_x, public_value_y)

    def _private_value_to_cryptography_private_numbers(self, private_value):
        """
        Return an instance of cryptography PrivateNumbers from the decimal private_value
        """
        public_value_x, public_value_y = self._private_value_to_public_values(private_value)
        public_numbers = PublicKey._public_values_to_cryptography_public_numbers(public_value_x, public_value_y)
        private_numbers = ec.EllipticCurvePrivateNumbers(private_value, public_numbers)
        return private_numbers

    @staticmethod
    def _cryptography_private_key_from_private_numbers(private_numbers):
        """
        Return an instace of cryptography PrivateKey from a cryptography instance of PrivateNumbers
        """
        return private_numbers.private_key(default_backend())


class PublicKey(object):

    def __init__(self, key):
        """
        Instantiate the public key with the compressed public value encoded in base58
        """
        public_value_x, public_value_y = self.decode(key)
        public_numbers = self._public_values_to_cryptography_public_numbers(public_value_x, public_value_y)
        self.public_key = self._criptography_public_key_from_public_numbers(public_numbers)

    def verify(self, data, signature):
        verifier = self.public_key.verifier(binascii.unhexlify(signature), ec.ECDSA(hashes.SHA256()))
        verifier.update(data.encode('utf-8'))
        try:
            verifier.verify()
        except InvalidSignature:
            return False

        return True

    @staticmethod
    def encode(public_value_x, public_value_y):
        """
        Encode the public key represented by the decimal values x and y to base58
        """
        public_value_compressed_hex = bitcoin.encode_pubkey([public_value_x, public_value_y], 'hex_compressed')
        public_value_compressed_base58 = base58.b58encode(bytes.fromhex(public_value_compressed_hex))
        return public_value_compressed_base58

    @staticmethod
    def decode(public_value_compressed_base58):
        """
        Decode the base58 public_value to the decimal x and y values
        """
        public_value_compressed_hex = binascii.hexlify(base58.b58decode(public_value_compressed_base58))
        public_value_x, public_value_y = bitcoin.decode_pubkey(public_value_compressed_hex.decode())
        return (public_value_x, public_value_y)

    @staticmethod
    def _public_values_to_cryptography_public_numbers(public_value_x, public_value_y):
        """
        Return an instance of cryptography PublicNumbers from the decimal x and y values
        """
        public_numbers = ec.EllipticCurvePublicNumbers(public_value_x, public_value_y, ec.SECP256K1())
        return public_numbers

    def _criptography_public_key_from_public_numbers(self, public_numbers):
        """
        Return an instance of cryptography PublicKey from a cryptography instance of PublicNumbers
        """
        return public_numbers.public_key(default_backend())


def generate_key_pair():
    """
    Generate a new key pair and return the pair encoded in base58
    """
    # Private key
    private_key = ec.generate_private_key(ec.SECP256K1, default_backend())
    private_value = private_key.private_numbers().private_value
    private_value_base58 = PrivateKey.encode(private_value)

    # Public key
    public_key = private_key.public_key()
    public_value_x, public_value_y = public_key.public_numbers().x, public_key.public_numbers().y
    public_value_compressed_base58 = PublicKey.encode(public_value_x, public_value_y)

    return (private_value_base58, public_value_compressed_base58)


def hash_data(data):
    """Hash the provided data using SHA3-256"""

    return sha3.sha3_256(data.encode()).hexdigest()


