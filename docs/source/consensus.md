# BigchainDB Consensus Plugins
TODO: Write this section

A quick example of a plugin that adds nonsense rules:

```python
from bigchaindb.consensus import BaseConsensusRules

class SillyConsensusRules(BaseConsensusRules):

    @staticmethod
    def validate_transaction(bigchain, transaction):
        transaction = super().validate_transaction(bigchain, transaction)
        # I only like transactions whose timestamps are even.
        if transaction['transaction']['timestamp'] % 2 != 0:
            raise StandardError("Odd... very odd indeed.")
        return transaction

    @staticmethod
    def validate_block(bigchain, block):
        block = super().validate_block(bigchain, block)
        # I don't trust Alice, I think she's shady.
        if block['block']['node_pubkey'] == '<ALICE_PUBKEY>':
            raise StandardError("Alice is shady, everybody ignore her blocks!")

       return block
```
