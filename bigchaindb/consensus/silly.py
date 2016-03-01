import bigchaindb.exceptions as exceptions
from bigchaindb.crypto import hash_data
from bigchaindb.consensus import AbstractConsensusRules


class SillyConsensusRules(AbstractConsensusRules):

    @classmethod
    def validate_transaction(cls, bigchain, transaction):
        # I only like transactions whose timestamps are even.
        if transaction['transaction']['timestamp'] % 2 != 0:
            raise StandardError("Odd... very odd indeed.")
        return transaction

    @classmethod
    def validate_block(cls, bigchain, transaction):
        # I don't trust Alice, I think she's shady.
        if block['block']['node_pubkey'] == '<ALICE_PUBKEY>':
            raise StandardError("Alice is shady, everybody ignore her blocks!")

        return block
