# The Block Model

Every block contains up to 1000 transactions. A block has the following structure:

```json
{
    "id": "<hash of block>",
    "block": {
        "timestamp": "<block-creation timestamp>",
        "transactions": ["<list of transactions>"],
        "node_pubkey": "<public key of the node creating the block>",
        "voters": ["<list of federation nodes public keys>"]
    },
    "signature": "<signature of block>",
}
```

- `id`: The hash of the serialized `block` (i.e. the `timestamp`, `transactions`, `node_pubkey`, and `voters`). This is also a database primary key; that's how we ensure that all blocks are unique.
- `block`:
    - `timestamp`: The Unix time when the block was created. It's provided by the node that created the block. See [the page about timestamps](https://docs.bigchaindb.com/en/latest/timestamps.html).
    - `transactions`: A list of the transactions included in the block.
    - `node_pubkey`: The public key of the node that create the block.
    - `voters`: A list of public keys of federation nodes. Since the size of the 
      federation may change over time, this will tell us how many nodes existed
      in the federation when the block was created, so that at a later point in
      time we can check that the block received the correct number of votes.
- `signature`: Signature of the block by the node that created the block. (To create the signature, the node serializes the block contents and signs that with its private key.)
