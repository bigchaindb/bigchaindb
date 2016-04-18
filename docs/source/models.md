# The Transaction, Block and Vote Models

Transactions, blocks and votes are represented using JSON documents with the following models (schemas). See [the section on cryptography](cryptography.html) for more information about how we calculate hashes and signatures.

## The Transaction Model

```json
{
    "id": "<sha3 hash>",
    "version": "<transaction version number>",
    "transaction": {
        "fulfillments": ["<list of <fullfillment>"],
        "conditions": ["<list of <condition>"],
        "operation": "<string>",
        "timestamp": "<timestamp from client>",
        "data": {
            "hash": "<SHA3-256 hash hexdigest of payload>",
            "payload": "<generic json document>"
        }
    }
}
```

A transaction is an operation between the `current_owner` and the `new_owner` over the digital content described by `hash`. For example if could be a transfer of ownership of the digital content `hash`

- **Transaction header**:
    - `id`: sha3 hash of the transaction. The `id` is also the DB primary key.
    - `version`: Version of the transaction. For future compability with changes in the transaction model.
- **Transaction body**:
    - `fulfillments`: List of fulfillments. Each _fulfillment_ contains a pointer to a unspent digital asset
    and a _crypto fulfillment_ that satisfies a spending condition set on the unspent digital asset. A _fulfillment_
    is usually a signature proving the ownership of the digital asset.
    See [conditions and fulfillments](models.md#conditions-and-fulfillments)
    - `conditions`: List of conditions. Each _condition_ a _crypto condition_ that needs to be fulfilled by the
    new owner in order to spend the digital asset.
    See [conditions and fulfillments](models.md#conditions-and-fulfillments)
    - `operation`: String representation of the operation being performed (CREATE, TRANSFER, ...) this will define how
    the transactions should be validated
    - `timestamp`: Time of creation of the transaction in UTC. It's provided by the client.
    - `data`: JSON object describing the asset (digital content). It contains at least the field `hash` which is a
    sha3 hash of the digital content.

## Conditions and Fulfillments

### Conditions

##### Simple Signature

If there is only one _new owner_ the condition will be a single signature condition.

```json
{
    "cid": "<condition index>",
    "condition": {
        "details": {
            "bitmask": "<explain>",
            "public_key": "<explain>",
            "signature": null,
            "type": "fulfillment",
            "type_id": "<explain>"
        },
        "uri": "<explain>"
    },
    "new_owners": ["<explain>"]
}
```

- **Condition header**:
    - `cid`: Condition index so that we can reference this output as an input to another transaction. It also matches
    the input `fid`, making this the condition to fulfill in order to spend the digital asset used as input with `fid`
    - `new_owners`: List of public keys of the new owners.
- **Condition body**:
    - `bitmask`:
    - `public_key`:
    - `signature`:
    - `type`:
    - `type_id`:
    - `uri`:

##### Multi Signature

If there are multiple _new owners_ by default we create a condition requiring a signature from each new owner in order
to spend the digital asset.

Example of a condition with two _new owners_:
```json
{
    "cid": "<condition index>",
    "condition": {
        "details": {
            "bitmask": 41,
            "subfulfillments": [
                {
                    "bitmask": 32,
                    "public_key": "<new owner 1 public key>",
                    "signature": null,
                    "type": "fulfillment",
                    "type_id": 4,
                    "weight": 1
                },
                {
                    "bitmask": 32,
                    "public_key": "<new owner 2 public key>",
                    "signature": null,
                    "type": "fulfillment",
                    "type_id": 4,
                    "weight": 1
                }
            ],
            "threshold": 2,
            "type": "fulfillment",
            "type_id": 2
        },
        "uri": "cc:2:29:ytNK3X6-bZsbF-nCGDTuopUIMi1HCyCkyPewm6oLI3o:206"},
        "new_owners": [
            "<new owner 1 public key>",
            "<new owner 2 public key>"
        ]
}
```

- `subfulfillments`:
    - `weight`:
- `threshold`:


### Fulfillments

##### Simple Signature

If there is only one _current owner_ the fulfillment will be a single signature fulfillment.

```json
{
    "current_owners": ["<Public Key>"],
    "fid": 0,
    "fulfillment": "cf:4:RxFzIE679tFBk8zwEgizhmTuciAylvTUwy6EL6ehddHFJOhK5F4IjwQ1xLu2oQK9iyRCZJdfWAefZVjTt3DeG5j2exqxpGliOPYseNkRAWEakqJ_UrCwgnj92dnFRAEE",
    "input": {
        "cid": 0,
        "txid": "11b3e7d893cc5fdfcf1a1706809c7def290a3b10b0bef6525d10b024649c42d3"
    }
}
```

- `fid`: Fulfillment index. It matches a `cid` in the conditions with a new _crypto condition_ that the new owner(s)
need to fulfill to spend this digital asset
- `current_owners`: Public key of the current owner(s)
- `fulfillment`:
- `input`: Pointer to the digital asset and condition of a previous transaction
    - `cid`: Condition index
    - `txid`: Transaction id

## The Block Model

```json
{
    "id": "<sha3 hash of the serialized block contents>",
    "block": {
        "timestamp": "<block-creation timestamp>",
        "transactions": ["<list of transactions>"],
        "node_pubkey": "<public key of the node creating the block>",
        "voters": ["<list of federation nodes public keys>"]
    },
    "signature": "<signature of the block>",
    "votes": ["<list of votes>"]
}
```

Still to be defined when new blocks are created (after x number of transactions, or after x amount of seconds, 
or both).

A block contains a group of transactions and includes the hash of the hash of the previous block to build the chain.

- `id`: sha3 hash of the contents of `block` (i.e. the timestamp, list of transactions, node_pubkey, and voters). This is also a RethinkDB primary key; that's how we ensure that all blocks are unique.
- `block`: The actual block
    - `timestamp`: timestamp when the block was created. It's provided by the node that created the block.
    - `transactions`: the list of transactions included in the block
    - `node_pubkey`: the public key of the node that create the block
    - `voters`: list public keys of the federation nodes. Since the size of the 
      federation may change over time this will tell us how many nodes existed
      in the federation when the block was created so that in a later point in
      time we can check that the block received the correct number of votes.
- `signature`: Signature of the block by the node that created the block (i.e. To create it, the node serialized the block contents and signed that with its private key)
- `votes`: Initially an empty list. New votes are appended as they come in from the nodes.

## The Vote Model

Each node must generate a vote for each block, to be appended to that block's `votes` list. A vote has the following structure:

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
    "signature": "<signature of vote block>"
}
```

Note: The `invalid_reason` was not being used as of v0.1.3.
