# The Transaction, Block and Vote Models

Transactions, blocks and votes are represented using JSON documents with the following models (schemas).

## The Transaction Model

```json
{
    "id": "<sha3 hash>",
    "transaction": {
        "current_owner": "<pub-key>",
        "new_owner": "<pub-key>",
        "input": "<sha3 hash>",
        "operation": "<string>",
        "timestamp": "<timestamp>",
        "data": {
            "hash": "<sha3 hash>",
            ...
        }
    },
    "signature": "<ECDSA signature of the transaction>"
}
```

A transaction is an operation between the `current_owner` and the `new_owner` over the digital content described by `hash`. For example if could be a transfer of ownership of the digital content `hash`

- `id`: sha3 hash of the transaction and rethinkdb primary key. By using the hash of the transaction of the 
primary key we eliminate the problem of duplicated transactions, if for some reason two nodes decide to create the 
same transaction
- `current_owner`: Public key of the current owner of the digital content with hash `hash`
- `new_owner`: Public key of the new owner of the digital content with hash `hash`
- `input`: sha3 hash of the transaction in which the content was transfered to the user (similar to input in 
the blockchain). Right now we will assume that there is only one input per transaction to simplify the prototype. 
This can be changed in the future to allow multiple inputs per transaction.
- `operation`: String representation of the operation being performed (REGISTER, TRANSFER, ...) this will define how
the transactions should be validated
- `timestamp`: Time of creation of the transaction in UTC
- `data`: Json object describing the asset (digital content). It contains at least the field `hash` which is a 
sha3 hash of the digital content.
- `signature`: ECDSA signature of the transaction with the `current_owner` private key

## The Block Model

```json
{
    "id": "<sha3 hash of the list of transactions + timestamp + nodes_pubkeys>",
    "block": {
        "timestamp": "<RethinkDB timestamp>",
        "transactions": ["<list of transactions>"],
        "node_pubkey": "<public key of the node creating the block>",
        "voters": ["<list of federation nodes pulic keys>"]
    },
    "signature": "<signature of the block>",
    "votes": []
}
```

Still to be defined when new blocks are created (after x number of transactions, or after x amount of seconds, 
or both).
A block contains a group of transactions and includes the hash of the hash of the previous block to build the chain.

- `id`: sha3 hash of the current block. This is also a rethinkdb primary key, this way we make sure that all blocks are unique.
- `block`: The actual block
    - `timestamp`: timestamp when the block was created
    - `transactions`: the list of transactions included in the block
    - `node_pubkey`: the public key of the node that create the block
    - `voters`: list public keys of the federation nodes. Since the size of the
      federation may change over time this will tell us how many nodes existed
      in the federation when the block was created so that in a later point in
      time we can check that the block received the correct number of votes.
- `signature`: Signature of the block by the node that created the block
- `votes`: Initially an empty list. Nodes in the voters list will append to it
  has they vote on the block


## The Vote Model

This is the structure that each node will append to the block `votes` list.

```json
{
    "node_pubkey": "<the pubkey of the voting node>",
    "vote": {
        "voting_for_block": "<id of the block the node is voting for>",
        "previous_block": "<id of the block previous to this one>",
        "is_block_valid": "<true|false>",
        "invalid_reason": "<None|DOUBLE_SPEND|TRANSACTIONS_HASH_MISMATCH|NODES_PUBKEYS_MISMATCH",
        "timestamp": "<timestamp of the voting action>"
    },
    "signature": "<ECDSA signature of vote block>"
}
```
