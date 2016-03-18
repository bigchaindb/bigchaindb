from abc import abstractmethod

from bigchaindb.crypto.fulfillment import Fulfillment
from bigchaindb.crypto.iostream import Hasher


class BaseSha256Fulfillment(Fulfillment):

    def generate_hash(self):
        """
        Calculate condition hash.

        This method is called internally by `condition`. It calculates the
        condition hash by hashing the hash payload.

        Return:
            Buffer: Result from hashing the hash payload.
        """
        hasher = Hasher('sha256')
        self.write_hash_payload(hasher)
        return hasher.digest()  # remove padding

    @abstractmethod
    def write_hash_payload(self, hasher):
        raise NotImplementedError
