# The Transaction, Block and Vote Models

BigchainDB stores all its records in JSON documents.

The three main kinds of records are transactions, blocks and votes. 
_Transactions_ are used to register, issue, create or transfer things (e.g. assets). Multiple transactions are combined with some other metadata to form _blocks_. Nodes append _votes_ to blocks. This section is a reference on the details of transactions, blocks and votes.

Below we often refer to cryptographic hashes, keys and signatures. The details of those are covered in [the section on cryptography](../appendices/cryptography.html).


## Transaction Concepts

Transactions are the most basic kind of record stored by BigchainDB. There are two kinds: creation transactions and transfer transactions.

A _creation transaction_ can be used to register, issue, create or otherwise initiate the history of a single thing (or asset) in BigchainDB. For example, one might register an identity or a creative work. The things are often called "assets" but they might not be literal assets. A creation transaction also establishes the initial owner or owners of the asset. Only a federation node can create a valid creation transaction (but it's usually made based on a message from a client).

Currently, BigchainDB only supports indivisible assets. You can't split an asset apart into multiple assets, nor can you combine several assets together into one. [Issue #129](https://github.com/bigchaindb/bigchaindb/issues/129) is an enhancement proposal to support divisible assets.

A _transfer transaction_ can transfer one or more assets to new owners.

BigchainDB works with the [Interledger Protocol (ILP)](https://interledger.org/), a protocol for transferring assets between different ledgers, blockchains or payment systems.

The owner(s) of an asset can specifiy conditions (ILP crypto-conditions) which others must fulfill (satisfy) in order to become the new owner(s) of the asset. For example, a crypto-condition might require a signature from the owner, or from m-of-n owners (a threshold condition, e.g. 3-of-4).

When someone creates a transfer transaction with the goal of changing an asset's owners, they must fulfill the asset's current crypto-conditions (i.e. in a fulfillment), and they must provide new conditions (including the list of new owners).

Every create transaction contains exactly one fulfillment-condition pair. A transfer transaction can contain multiple fulfillment-condition pairs: one per asset transferred. Every fulfillment in a transfer transaction (input) must correspond to a condition (output) in a previous transaction. The diagram below illustrates some of these concepts: transactions are represented by light grey boxes, fulfillments have a label like `f:0`, and conditions have a label like `c:0`.

![Tracking the stories of three assets](../_static/stories_3_assets.png)

When a node is asked to check the validity of a transaction, it must do several things; the main things are:

* schema validation,
* double-spending checks (for transfer transactions),
* hash validation (i.e. is the calculated transaction hash equal to its id?), and
* validation of all fulfillments, including validation of cryptographic signatures if they’re among the conditions.

The full details of transaction validation can be found in the code for `validate_transaction()` in the `BaseConsensusRules` class of [`consensus.py`](https://github.com/bigchaindb/bigchaindb/blob/master/bigchaindb/consensus.py) (unless other validation rules are being used by a federation, in which case those should be consulted instead).


## Some Words of Caution

BigchainDB is still in the early stages of development. The data models described below may change substantially before BigchainDB reaches a production-ready state (i.e. version 1.0 and higher).

Also, note that timestamps come from clients and nodes. Unless you have some reason to believe that some timestamps are correct or meaningful, we advise you to ignore them (i.e. don't make any decisions based on them). (You might trust a timestamp, for example, if it came from a trusted timestamping service and it is embedded in the transaction data `payload` along with the signature from the timestamping service. You might trust node timestamps if you know all the nodes are running NTP servers.)


## The Transaction Model

```json
{
    "id": "<hash of transaction, excluding signatures (see explanation)>",
    "version": "<version number of the transaction model>",
    "transaction": {
        "fulfillments": ["<list of fulfillments>"],
        "conditions": ["<list of conditions>"],
        "operation": "<string>",
        "timestamp": "<timestamp from client>",
        "data": {
            "hash": "<hash of payload>",
            "payload": "<any JSON document>"
        }
    }
}
```

Here's some explanation of the contents of a transaction:

- `id`: The hash of everything inside the serialized `transaction` body (i.e. `fulfillments`, `conditions`, `operation`, `timestamp` and `data`; see below), with one wrinkle: for each fulfillment in `fulfillments`, `fulfillment` is set to `null`. The `id` is also the database primary key.
- `version`: Version number of the transaction model, so that software can support different transaction models.
- `transaction`:
    - `fulfillments`: List of fulfillments. Each _fulfillment_ contains a pointer to an unspent asset
    and a _crypto fulfillment_ that satisfies a spending condition set on the unspent asset. A _fulfillment_
    is usually a signature proving the ownership of the asset.
    See [Conditions and Fulfillments](#conditions-and-fulfillments) below.
    - `conditions`: List of conditions. Each _condition_ is a _crypto-condition_ that needs to be fulfilled by a transfer transaction in order to transfer ownership to new owners.
    See [Conditions and Fulfillments](#conditions-and-fulfillments) below.
    - `operation`: String representation of the operation being performed (currently either "CREATE" or "TRANSFER"). It determines how the transaction should be validated.
    - `timestamp`: Time of creation of the transaction in UTC. It's provided by the client.
    - `data`:
        - `hash`: The hash of the serialized `payload`.
        - `payload`: Can be any JSON document. It may be empty in the case of a transfer transaction.

Later, when we get to the models for the block and the vote, we'll see that both include a signature (from the node which created it). You may wonder why transactions don't have signatures... The answer is that they do! They're just hidden inside the `fulfillment` string of each fulfillment. A creation transaction is signed by the node that created it. A transfer transaction is signed by whoever currently controls or owns it.

What gets signed? For each fulfillment in the transaction, the "fullfillment message" that gets signed includes the `operation`, `timestamp`, `data`, `version`, `id`, corresponding `condition`, and the fulfillment itself, except with its fulfillment string set to `null`. The computed signature goes into creating the `fulfillment` string of the fulfillment.

One other note: Currently, transactions contain only the public keys of asset-owners (i.e. who own an asset or who owned an asset in the past), inside the conditions and fulfillments. A transaction does _not_ contain the public key of the client (computer) which generated and sent it to a BigchainDB node. In fact, there's no need for a client to _have_ a public/private keypair. In the future, each client may also have a keypair, and it may have to sign each sent transaction (using its private key); see [Issue #347 on GitHub](https://github.com/bigchaindb/bigchaindb/issues/347). In practice, a person might think of their keypair as being both their "ownership-keypair" and their "client-keypair," but there is a difference, just like there's a difference between Joe and Joe's computer.


## Conditions and Fulfillments

An aside: In what follows, the list of `new_owners` (in a condition) is always who owned the asset at the time the transaction completed, but before the next transaction started. The list of `current_owners` (in a fulfillment) is always equal to the list of `new_owners` in that asset's previous transaction.

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

If there are multiple _new owners_, they can create a ThresholdCondition requiring a signature from each of them in order
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

- `fid`: Fulfillment index. It matches a `cid` in the conditions with a new _crypto-condition_ that the new owner
  needs to fulfill to spend this asset.
- `current_owners`: A list of public keys of the current owners; in this case it has just one public key.
- `fulfillment`: A crypto-conditions URI that encodes the cryptographic fulfillments like signatures and others, see [crypto-conditions](https://interledger.org/five-bells-condition/spec.html).
- `input`: Pointer to the asset and condition of a previous transaction
    - `cid`: Condition index
    - `txid`: Transaction id

## The Block Model

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
    "votes": ["<list of votes>"]
}
```

- `id`: The hash of the serialized `block` (i.e. the `timestamp`, `transactions`, `node_pubkey`, and `voters`). This is also a database primary key; that's how we ensure that all blocks are unique.
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
    "signature": "<signature of vote>"
}
```

Note: The `invalid_reason` was not being used as of v0.1.3 and may be dropped in a future version of BigchainDB.
