# The Transaction, Block and Vote Models

Transactions, blocks and votes are represented using JSON documents with the following models (schemas). See [the section on cryptography](cryptography.html) for more information about how we calculate hashes and signatures.

## The Transaction Model

```json
{
    "id": "<SHA3-256 hash hexdigest of transaction (below)>",
    "version": "<version number of the transaction model>",
    "transaction": {
        "fulfillments": ["<list of fulfillments>"],
        "conditions": ["<list of conditions>"],
        "operation": "<string>",
        "timestamp": "<timestamp from client>",
        "data": {
            "hash": "<SHA3-256 hash hexdigest of payload>",
            "payload": "<any JSON document>"
        }
    }
}
```

Transactions are the basic records stored by BigchainDB. There are two kinds:

1. A "CREATE" transaction creates a new asset. It has `"operation": "CREATE"`. The `payload` or a "CREATE" transaction describes, encodes, or links to the asset in some way.
2. A "TRANSFER" transaction transfers one or more assets. It has `"operation": "TRANSFER"`. The `payload` of a "TRANSFER" transaction can be empty, but it can also be used for use-case-specific information (e.g. different kinds of transfers).

Here's some explanation of the contents of a transaction:

- `id`: The SHA3-256 hash hexdigest of everything inside the serialized `transaction` body (i.e. `fulfillments`, `conditions`, `operation`, `timestamp` and `data`; see below). The `id` is also the database primary key.
- `version`: Version number of the transaction model, so that software can support different transaction models.
- `transaction`:
    - `fulfillments`: List of fulfillments. Each _fulfillment_ contains a pointer to an unspent asset
    and a _crypto fulfillment_ that satisfies a spending condition set on the unspent asset. A _fulfillment_
    is usually a signature proving the ownership of the asset.
    See [Conditions and Fulfillments](#conditions-and-fulfillments) below.
    - `conditions`: List of conditions. Each _condition_ is a _crypto condition_ that needs to be fulfilled by the
    new owner in order to spend the asset.
    See [Conditions and Fulfillments](#conditions-and-fulfillments) below.
    - `operation`: String representation of the operation being performed (currently either "CREATE" or "TRANSFER"). It determines how
    the transaction should be validated.
    - `timestamp`: Time of creation of the transaction in UTC. It's provided by the client.
    - `data`:
        - `hash`: The SHA3-256 hash hexdigest of the serialized `payload`.
        - `payload`: Can be any JSON document. Its meaning depends on the whether the transaction 
    is a "CREATE" or "TRANSFER" transaction; see above.

## Conditions and Fulfillments

### Conditions

#### One New Owner

If there is only one _new owner_, the condition will be a single-signature condition.

```json
{
    "cid": "<condition index>",
    "condition": {
        "details": {
            "bitmask": "<base16 int>",
            "public_key": "<new owner public key>",
            "signature": null,
            "type": "fulfillment",
            "type_id": "<base16 int>"
        },
        "uri": "<string>"
    },
    "new_owners": ["<new owner public key>"]
}
```

- **Condition header**:
    - `cid`: Condition index so that we can reference this output as an input to another transaction. It also matches
    the input `fid`, making this the condition to fulfill in order to spend the asset used as input with `fid`.
    - `new_owners`: A list containing one item: the public key of the new owner.
- **Condition body**:
    - `bitmask`: A set of bits representing the features required by the condition type.
    - `public_key`: The _new_owner's_ public key.
    - `type_id`: The fulfillment type ID; see the [ILP spec](https://interledger.org/five-bells-condition/spec.html).
    - `uri`: Binary representation of the condition using only URL-safe characters.

#### Multiple New Owners

If there are multiple _new owners_, we can create a ThresholdCondition requiring a signature from each new owner in order
to spend the asset. For example:

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

- `subfulfillments`: a list of fulfillments
    - `weight`: integer weight for each subfulfillment's contribution to the threshold
- `threshold`: threshold to reach for the subfulfillments to reach a valid fulfillment 

The `weight`s and `threshold` could be adjusted. For example, if the `threshold` was changed to 1 above, then only one of the new owners would have to provide a signature to spend the asset.

### Fulfillments

#### One Current Owner

If there is only one _current owner_, the fulfillment will be a single-signature fulfillment.

```json
{
    "current_owners": ["<public key of current owner>"],
    "fid": 0,
    "fulfillment": "cf:4:RxFzIE679tFBk8zwEgizhmTuciAylvTUwy6EL6ehddHFJOhK5F4IjwQ1xLu2oQK9iyRCZJdfWAefZVjTt3DeG5j2exqxpGliOPYseNkRAWEakqJ_UrCwgnj92dnFRAEE",
    "input": {
        "cid": 0,
        "txid": "11b3e7d893cc5fdfcf1a1706809c7def290a3b10b0bef6525d10b024649c42d3"
    }
}
```

- `fid`: Fulfillment index. It matches a `cid` in the conditions with a new _crypto condition_ that the new owner
  needs to fulfill to spend this asset.
- `current_owners`: A list of public keys of the current owners; in this case it has just one public key.
- `fulfillment`: A cryptoconditions URI that encodes the cryptographic fulfillments like signatures and others, see crypto-conditions.
- `input`: Pointer to the asset and condition of a previous transaction
    - `cid`: Condition index
    - `txid`: Transaction id

## The Block Model

```json
{
    "id": "<SHA3-256 hash hexdigest of the serialized block contents>",
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

- `id`: SHA3-256 hash hexdigest of the contents of `block` (i.e. the timestamp, list of transactions, node_pubkey, and voters). This is also a database primary key; that's how we ensure that all blocks are unique.
- `block`:
    - `timestamp`: Timestamp when the block was created. It's provided by the node that created the block.
    - `transactions`: A list of the transactions included in the block.
    - `node_pubkey`: The public key of the node that create the block.
    - `voters`: A list of public keys of federation nodes. Since the size of the 
      federation may change over time, this will tell us how many nodes existed
      in the federation when the block was created, so that at a later point in
      time we can check that the block received the correct number of votes.
- `signature`: Signature of the block by the node that created the block. (To create the signature, the node serializes the block contents and signs that with its private key.)
- `votes`: Initially an empty list. New votes are appended as they come in from the nodes.

## The Vote Model

Each node must generate a vote for each block, to be appended to that block's `votes` list. A vote has the following structure:

```json
{
    "node_pubkey": "<the public key of the voting node>",
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

Note: The `invalid_reason` was not being used as of v0.1.3 and may be dropped in a future version of BigchainDB.
