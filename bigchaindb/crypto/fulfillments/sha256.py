from bigchaindb.crypto.fulfillments.base_sha256 import BaseSha256Fulfillment
from bigchaindb.crypto.buffer import Hasher, Reader, Writer, Predictor


class Sha256Fulfillment(BaseSha256Fulfillment):

    _bitmask = 0x01

    def __init__(self):
        self._preimage = None

    @property
    def preimage(self):
        return self._preimage

    @preimage.setter
    def preimage(self, value):
        """
        Provide a preimage.

        The preimage is the only input to a SHA256 hashlock condition.

        Note that the preimage should contain enough (pseudo-random) data in order
        to be difficult to guess. A sufficiently large secret seed and a
        cryptographically secure pseudo-random number generator (CSPRNG) can be
        used to avoid having to store each individual preimage.

        Args:
             value: Secret data that will be hashed to form the condition.
        """
        # TODO: Verify preimage
        self._preimage = value

    def write_hash_payload(self, hasher):
        """
        Generate the contents of the condition hash.

        Writes the contents of the condition hash to a Hasher. Used internally by `getCondition`.

        HASH = SHA256(PREIMAGE)

        Args:
             hasher (Hasher): Destination where the hash payload will be written.
        """
        if not isinstance(hasher, Hasher):
            raise TypeError('hasher must be a Hasher instance')
        if self.preimage is None:
            raise ValueError('Could not calculate hash, no preimage provided')
        hasher.write(self.preimage)

    def parse_payload(self, reader):
        """
        Parse the payload of a SHA256 hashlock fulfillment.

        Read a fulfillment payload from a Reader and populate this object with that fulfillment.

        FULFILLMENT_PAYLOAD =
            VARBYTES PREIMAGE

        Args:
            reader (Reader): Source to read the fulfillment payload from.
        """
        if not isinstance(reader, Reader):
            raise TypeError('reader must be a Reader instance')
        self.preimage = reader.read_var_bytes()

    def write_payload(self, writer):
        """
        Generate the fulfillment payload.

        This writes the fulfillment payload to a Writer.

        Args:
            writer (Writer): Subject for writing the fulfillment payload.
        """
        if not isinstance(writer, (Writer, Predictor)):
            raise TypeError('writer must be a Writer instance')
        if self.preimage is None:
            raise ValueError('Preimage must be specified')

        writer.write_var_bytes(self.preimage)
        return writer

    def validate(self):
        """
        Validate this fulfillment.

        For a SHA256 hashlock fulfillment, successful parsing implies that the
        fulfillment is valid, so this method is a no-op.

        Returns:
             boolean: Validation result
        """
        return True
