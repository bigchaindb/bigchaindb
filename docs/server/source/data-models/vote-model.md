# The Vote Model

A vote has the following structure:

```json
{
    "id": "<RethinkDB-generated ID for the vote>",
    "node_pubkey": "<the public key of the voting node>",
    "vote": {
        "voting_for_block": "<id of the block the node is voting for>",
        "previous_block": "<id of the block previous to this one>",
        "is_block_valid": "<true|false>",
        "invalid_reason": "<None|DOUBLE_SPEND|TRANSACTIONS_HASH_MISMATCH|NODES_PUBKEYS_MISMATCH",
        "timestamp": "<Unix time when the vote was generated, provided by the voting node>"
    },
    "signature": "<signature of vote>"
}
```

Note: The `invalid_reason` was not being used and may be dropped in a future version of BigchainDB. See [Issue #217](https://github.com/bigchaindb/bigchaindb/issues/217) on GitHub.
