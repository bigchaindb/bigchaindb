import base58

from bigchaindb.crypto.ed25519 import ED25519PublicKey
from bigchaindb.crypto.fulfillments.base_sha256 import BaseSha256Fulfillment
from bigchaindb.crypto.iostream import Predictor


class Ed25519Sha256Fulfillment(BaseSha256Fulfillment):

    _bitmask = 0x08

    def __init__(self):
        self._message_prefix = None
        self._max_dynamic_message_length = None
        self._public_key = None
        self._message = None
        self._signature = None

    @property
    def message_prefix(self):
        return self._message_prefix

    @message_prefix.setter
    def message_prefix(self, value):
        """
        Set the fixed message prefix.

        The fixed prefix is the portion of the message that is determined when the
        condition is first created.

        Args:
            value (Buffer): Static portion of the message
        """
        if not isinstance(value, bytes):
            value = value.encode()
        self._message_prefix = value

    @property
    def max_dynamic_message_length(self):
        return self._max_dynamic_message_length

    @max_dynamic_message_length.setter
    def max_dynamic_message_length(self, value):
        """
        Set the maximum length of the dynamic message component.

        The dynamic message is the part of the signed message that is determined at
        fulfillment time. However, when the condition is first created, we need to
        know the maximum fulfillment length, which in turn requires us to put a
        limit on the length of the dynamic message component.

        If this method is not called, the maximum dynamic message length defaults to zero.

        Args:
             value (int): Maximum length in bytes
        """
        self._max_dynamic_message_length = value

    @property
    def public_key(self):
        return self._public_key

    @public_key.setter
    def public_key(self, value):
        """
        Set the public publicKey.

        This is the Ed25519 public key. It has to be provided as a buffer.

        Args:
            value (Buffer): publicKey Public Ed25519 publicKey
        """
        # TODO: Buffer
        # if not isinstance(value, Buffer):
        #     raise ValueError("public key must be a Buffer")
        if not isinstance(value, ED25519PublicKey):
            raise TypeError
        self._public_key = value

    @property
    def message(self):
        return self._message

    @message.setter
    def message(self, value):
        """
        Set the dynamic message portion.

        Part of the signed message (the suffix) can be determined when the condition is being fulfilled.

        Length may not exceed the maximum dynamic message length.

        Args:
            value (Buffer): Binary form of dynamic message.
        """
        # TODO: Buffer
        # if not isinstance(value, Buffer):
        #     raise ValueError("message must be a Buffer")
        if not isinstance(value, bytes):
            value = value.encode()
        self._message = value

    @property
    def signature(self):
        return self._signature

    @signature.setter
    def signature(self, value):
        """
        Set the signature.

        Instead of using the private key to sign using the sign() method, we can also generate the signature elsewhere
        and pass it in.

        Args:
            value (Buffer): 64-byte signature.
        """
        # TODO: Buffer
        # if not isinstance(value, Buffer):
        #     raise ValueError("signature must be a Buffer")
        self._signature = value

    def write_common_header(self, writer):
        """
        Write static header fields.

        Some fields are common between the hash and the fulfillment payload. This
        method writes those field to anything implementing the Writer interface.
        It is used internally when generating the hash of the condition, when
        generating the fulfillment payload and when calculating the maximum fulfillment size.

        Args:
            writer (Writer|Hasher|Predictor): Target for outputting the header.
        """
        if not self.public_key:
            raise ValueError

        writer.write_var_bytes(bytearray(self.public_key.public_key.to_bytes()))
        writer.write_var_bytes(self.message_prefix)
        writer.write_var_uint(self.max_dynamic_message_length)
        return writer

    def parse_payload(self, reader):
        """
        Parse the payload of an Ed25519 fulfillment.

        Read a fulfillment payload from a Reader and populate this object with that fulfillment.

        Args:
            reader (Reader): Source to read the fulfillment payload from.
        """
        self.public_key = \
            ED25519PublicKey(
                base58.b58encode(
                    reader.read_var_bytes()))
        self.message_prefix = reader.read_var_bytes()
        self.max_dynamic_message_length = reader.read_var_uint()
        self.message = reader.read_var_bytes()
        self.signature = reader.read_var_bytes()

    def write_payload(self, writer):
        """
        Generate the fulfillment payload.

        This writes the fulfillment payload to a Writer.

        COMMON_HEADER =
            VARBYTES PUBLIC_KEY
            VARBYTES MESSAGE_ID
            VARBYTES FIXED_PREFIX
            VARUINT DYNAMIC_MESSAGE_LENGTH

        FULFILLMENT_PAYLOAD =
            COMMON_HEADER
            VARBYTES DYNAMIC_MESSAGE
            VARBYTES SIGNATURE

        Args:
            writer (Writer): Subject for writing the fulfillment payload.
        """
        self.write_common_header(writer)
        writer.write_var_bytes(self.message)
        writer.write_var_bytes(self.signature)
        return writer

    def write_hash_payload(self, hasher):
        """
        Generate the contents of the condition hash.

        Writes the contents of the condition hash to a Hasher. Used internally by `condition`.

        COMMON_HEADER =
            VARBYTES PUBLIC_KEY
            VARBYTES MESSAGE_ID
            VARBYTES FIXED_PREFIX
            VARUINT DYNAMIC_MESSAGE_LENGTH

        HASH = SHA256(
            COMMON_HEADER
        )

        Args:
            hasher (Hasher): Destination where the hash payload will be written.
        """
        hasher.write_var_uint(self.bitmask)
        return self.write_common_header(hasher)

    def calculate_max_fulfillment_length(self):
        """
        Calculates the longest possible fulfillment length.

        The longest fulfillment for an Ed25519 condition is the length of a
        fulfillment where the dynamic message length equals its maximum length.

        Return:
            Maximum length of the fulfillment payload
        """

        predictor = Predictor()

        if not self.public_key:
            raise ValueError('Requires a public key')

        # Calculate the length that the common header would have
        self.write_common_header(predictor)

        # Message suffix
        predictor.write_var_uint(self.max_dynamic_message_length)
        predictor.skip(self.max_dynamic_message_length)

        # Signature
        predictor.write_var_bytes(self.public_key.public_key.to_bytes())

        return predictor.size

    def sign(self, private_key):
        """
        Sign the message.

        This method will take the currently configured values for the message
        prefix and suffix and create a signature using the provided Ed25519 private key.

        Args:
            private_key (string) Ed25519 private key
        """
        # TODO: Buffer
        sk = private_key
        vk = ED25519PublicKey(
            base58.b58encode(
                sk.private_key.get_verifying_key().to_bytes()))

        self.public_key = vk

        message = self.message_prefix + self.message

        # This would be the Ed25519ph version (JavaScript ES7):
        # const message = crypto.createHash('sha512')
        #   .update(Buffer.concat([this.messagePrefix, this.message]))
        #   .digest()

        self.signature = sk.sign(message, encoding=None)

    def validate(self):
        """
        Verify the signature of this Ed25519 fulfillment.

        The signature of this Ed25519 fulfillment is verified against the provided message and public key.

        Return:
            boolean: Whether this fulfillment is valid.
        """
        if not (self.message and self.signature):
            return False

        message = self.message_prefix + self.message
        return self.public_key.verify(message, self.signature, encoding=None)
