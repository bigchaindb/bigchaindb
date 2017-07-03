# The Vote Model

A vote has the following structure:

```json
{
    "node_pubkey": "<The public key of the voting node>",
    "vote": {
        "voting_for_block": "<ID of the block the node is voting on>",
        "previous_block": "<ID of the block previous to the block being voted on>",
        "is_block_valid": "<true OR false>",
        "invalid_reason": null,
        "timestamp": "<Unix time when the vote was generated, provided by the voting node>"
    },
    "signature": "<Cryptographic signature of vote>"
}
```

**Notes**

* Votes have no ID (or `"id"`), as far as users are concerned. (The backend database uses one internally, but it's of no concern to users and it's never reported to them via BigchainDB APIs.)

* At the time of writing, the value of `"invalid_reason"` was always `null`. In other words, it wasn't being used. It may be used or dropped in a future version of BigchainDB. See [Issue #217](https://github.com/bigchaindb/bigchaindb/issues/217) on GitHub.

* For more information about the vote `"timestamp"`, see [the page about timestamps in BigchainDB](https://docs.bigchaindb.com/en/latest/timestamps.html).

* For more information about how the `"signature"` is calculated, see [the page about cryptography in BigchainDB](../appendices/cryptography.html).
