# The Transaction, Block and Vote Models

BigchainDB stores all its records in JSON documents.

The three main kinds of records are transactions, blocks and votes. 
_Transactions_ are used to register, issue, create or transfer things (e.g. assets). Multiple transactions are combined with some other metadata to form _blocks_. Nodes vote on blocks. This section is a reference on the details of transactions, blocks and votes.

Below we often refer to cryptographic hashes, keys and signatures. The details of those are covered in [the section on cryptography](../appendices/cryptography.html).


## Some Words of Caution

BigchainDB is still in the early stages of development. The data models described below may change substantially before BigchainDB reaches a production-ready state (i.e. version 1.0 and higher).


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

To determine the current owner(s) of an asset, find the most recent valid transaction involving it, and then look at the list of owners in the _conditions_ (not the fulfillments).


### Transaction Validation

When a node is asked to check the validity of a transaction, it must do several things; the main things are:

* schema validation,
* double-spending checks (for transfer transactions),
* hash validation (i.e. is the calculated transaction hash equal to its id?), and
* validation of all fulfillments, including validation of cryptographic signatures if they’re among the conditions.

The full details of transaction validation can be found in the code for `validate_transaction()` in the `BaseConsensusRules` class of [`consensus.py`](https://github.com/bigchaindb/bigchaindb/blob/master/bigchaindb/consensus.py) (unless other validation rules are being used by a federation, in which case those should be consulted instead).


### Mutable and Immutable Assets

Assets can be mutable (changeable) or immutable. To change a mutable asset, you must create a valid transfer transaction with a payload specifying how it changed (or will change). The data structure (schema) of the change depends on the asset class. If you're inventing a new asset class, you can make up how to describe changes. For a mutable asset in an existing asset class, you should find out how changes are specified for that asset class. That's not something determined by BigchainDB.


## The Transaction Model

```json
{
    "id": "<hash of transaction, excluding signatures (see explanation)>",
    "transaction": {
        "version": "<version number of the transaction model>",
        "fulfillments": ["<list of fulfillments>"],
        "conditions": ["<list of conditions>"],
        "operation": "<string>",
        "timestamp": "<timestamp from client>",
        "asset": "<digital asset description (explained in the next section)>",
        "metadata": {
            "id": "<uuid>",
            "data": "<any JSON document>"
        }
    }
}
```

Here's some explanation of the contents of a transaction:

- `id`: The hash of everything inside the serialized `transaction` body (i.e. `fulfillments`, `conditions`, `operation`, `timestamp` and `data`; see below), with one wrinkle: for each fulfillment in `fulfillments`, `fulfillment` is set to `null`. The `id` is also the database primary key.
- `transaction`:
    - `version`: Version number of the transaction model, so that software can support different transaction models.
    - `fulfillments`: List of fulfillments. Each _fulfillment_ contains a pointer to an unspent asset
    and a _crypto fulfillment_ that satisfies a spending condition set on the unspent asset. A _fulfillment_
    is usually a signature proving the ownership of the asset.
    See [Conditions and Fulfillments](#conditions-and-fulfillments) below.
    - `conditions`: List of conditions. Each _condition_ is a _crypto-condition_ that needs to be fulfilled by a transfer transaction in order to transfer ownership to new owners.
    See [Conditions and Fulfillments](#conditions-and-fulfillments) below.
    - `operation`: String representation of the operation being performed (currently either "CREATE" or "TRANSFER"). It determines how the transaction should be validated.
    - `timestamp`: The Unix time when the transaction was created. It's provided by the client. See [the section on timestamps](timestamps.html).
	- `asset`: Definition of the digital asset. See next section.
    - `metadata`:
        - `id`: UUID version 4 (random) converted to a string of hex digits in standard form.
        - `data`: Can be any JSON document. It may be empty in the case of a transfer transaction.

Later, when we get to the models for the block and the vote, we'll see that both include a signature (from the node which created it). You may wonder why transactions don't have signatures... The answer is that they do! They're just hidden inside the `fulfillment` string of each fulfillment. A creation transaction is signed by the node that created it. A transfer transaction is signed by whoever currently controls or owns it.

What gets signed? For each fulfillment in the transaction, the "fullfillment message" that gets signed includes the `operation`, `timestamp`, `data`, `version`, `id`, corresponding `condition`, and the fulfillment itself, except with its fulfillment string set to `null`. The computed signature goes into creating the `fulfillment` string of the fulfillment.

One other note: Currently, transactions contain only the public keys of asset-owners (i.e. who own an asset or who owned an asset in the past), inside the conditions and fulfillments. A transaction does _not_ contain the public key of the client (computer) which generated and sent it to a BigchainDB node. In fact, there's no need for a client to _have_ a public/private keypair. In the future, each client may also have a keypair, and it may have to sign each sent transaction (using its private key); see [Issue #347 on GitHub](https://github.com/bigchaindb/bigchaindb/issues/347). In practice, a person might think of their keypair as being both their "ownership-keypair" and their "client-keypair," but there is a difference, just like there's a difference between Joe and Joe's computer.


## The Digital Asset Model
To avoid redundant data in transactions the digital asset model is different for `CREATE` and `TRANSFER` transactions.

The digital asset properties are defined at creation time in a `CREATE` transaction with the following model:
```json
{
    "id": "<uuid>",
    "divisible": "<true | false>",
    "updatable": "<true | false>",
    "refillable": "<true | false>",
    "data": "<json document>"
}
```

For `TRANSFER` transactions we only keep the asset id.
```json
{
    "id": "<uuid>",
}
```


- `id`: UUID version 4 (random) converted to a string of hex digits in standard form. Added server side.
- `divisible`: Whether the asset is divisible or not. Defaults to false.
- `updatable`: Whether the data in the asset can be updated in the future or not. Defaults to false.
- `refillable`: Whether the amount of the asset can change after its creation. Defaults to false.
- `data`: A user supplied JSON document with custom information about the asset. Defaults to null.
- _amount_: The amount of "shares". Only relevant if the asset is marked as divisible. Defaults to 1. The amount is not specified in the asset, but in the conditions (see next section).

At the time of this writing divisible, updatable, and refillable assets are not yet implemented.
See [Issue #487 on Github](https://github.com/bigchaindb/bigchaindb/issues/487)


## Conditions and Fulfillments

To create a transaction that transfers an asset to new owners, one must fulfill the asset’s current conditions (crypto-conditions). The most basic kinds of conditions are:

* **A hashlock condition:** One can fulfill a hashlock condition by providing the correct “preimage” (similar to a password or secret phrase)
* **A simple signature condition:** One can fulfill a simple signature condition by a providing a valid cryptographic signature (i.e. corresponding to the public key of an owner, usually)
* **A timeout condition:** Anyone can fulfill a timeout condition before the condition’s expiry time. After the expiry time, nobody can fulfill the condition. Another way to say this is that a timeout condition’s fulfillment is valid (TRUE) before the expiry time and invalid (FALSE) after the expiry time. Note: at the time of writing, timeout conditions are BigchainDB-specific (i.e. not part of the Interledger specs).

A more complex condition can be composed by using n of the above conditions as inputs to an m-of-n threshold condition (a logic gate which outputs TRUE iff m or more inputs are TRUE). If there are n inputs to a threshold condition:
* 1-of-n is the same as a logical OR of all the inputs
* n-of-n is the same as a logical AND of all the inputs

For example, one could create a condition requiring that m (of n) owners provide signatures before their asset can be transferred to new owners.

One can also put different weights on the inputs to threshold condition, along with a threshold that the weighted-sum-of-inputs must pass for the output to be TRUE. Weights could be used, for example, to express the number of shares that someone owns in an asset.

The (single) output of a threshold condition can be used as one of the inputs of other threshold conditions. This means that one can combine threshold conditions to build complex logical expressions, e.g. (x OR y) AND (u OR v).

Aside: In BigchainDB, the output of an m-of-n threshold condition can be inverted on the way out, so an output that would have been TRUE would get changed to FALSE (and vice versa). This enables the creation of NOT, NOR and NAND gates. At the time of writing, this “inverted threshold condition” is BigchainDB-specific (i.e. not part of the Interledger specs). It should only be used in combination with a timeout condition.

When one creates a condition, one can calculate its fulfillment length (e.g. 96). The more complex the condition, the larger its fulfillment length will be. A BigchainDB federation can put an upper limit on the allowed fulfillment length, as a way of capping the complexity of conditions (and the computing time required to validate them).

If someone tries to make a condition where the output of a threshold condition feeds into the input of another “earlier” threshold condition (i.e. in a closed logical circuit), then their computer will take forever to calculate the (infinite) “condition URI”, at least in theory. In practice, their computer will run out of memory or their client software will timeout after a while.

Aside: In what follows, the list of `owners_after` (in a condition) is always who owned the asset at the time the transaction completed, but before the next transaction started. The list of `owners_before` (in a fulfillment) is always equal to the list of `owners_after` in that asset's previous transaction.

### Conditions

#### One New Owner

If there is only one _new owner_, the condition will be a simple signature condition (i.e. only one signature is required).

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
    "owners_after": ["<new owner public key>"],
    "amount": "<int>"
}
```

- **Condition header**:
    - `cid`: Condition index so that we can reference this output as an input to another transaction. It also matches
    the input `fid`, making this the condition to fulfill in order to spend the asset used as input with `fid`.
    - `owners_after`: A list containing one item: the public key of the new owner.
	- `amount`: The amount of shares for a divisible asset to send to the new owners.
- **Condition body**:
    - `bitmask`: A set of bits representing the features required by the condition type.
    - `public_key`: The new owner's public key.
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
        "owners_after": [
            "owner 1 public key>",
            "owner 2 public key>"
        ]
}
```

- `subfulfillments`: a list of fulfillments
    - `weight`: integer weight for each subfulfillment's contribution to the threshold
- `threshold`: threshold to reach for the subfulfillments to reach a valid fulfillment 

The `weight`s and `threshold` could be adjusted. For example, if the `threshold` was changed to 1 above, then only one of the new owners would have to provide a signature to spend the asset.

### Fulfillments

#### One Current Owner

If there is only one _current owner_, the fulfillment will be a simple signature fulfillment (i.e. containing just one signature).

```json
{
    "owners_before": ["<public key of the owner before the transaction happened>"],
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
- `owners_before`: A list of public keys of the owners before the transaction; in this case it has just one public key.
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
}
```

- `id`: The hash of the serialized `block` (i.e. the `timestamp`, `transactions`, `node_pubkey`, and `voters`). This is also a database primary key; that's how we ensure that all blocks are unique.
- `block`:
    - `timestamp`: The Unix time when the block was created. It's provided by the node that created the block. See [the section on timestamps](timestamps.html).
    - `transactions`: A list of the transactions included in the block.
    - `node_pubkey`: The public key of the node that create the block.
    - `voters`: A list of public keys of federation nodes. Since the size of the 
      federation may change over time, this will tell us how many nodes existed
      in the federation when the block was created, so that at a later point in
      time we can check that the block received the correct number of votes.
- `signature`: Signature of the block by the node that created the block. (To create the signature, the node serializes the block contents and signs that with its private key.)

## The Vote Model

Each node must generate a vote for each block, to be appended the `votes` table. A vote has the following structure:

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
    "signature": "<signature of vote>",
}
```

Note: The `invalid_reason` was not being used as of v0.1.3 and may be dropped in a future version of BigchainDB.
