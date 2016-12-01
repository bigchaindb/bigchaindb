# Crypto-Conditions and Fulfillments

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

## (Crypto-) Conditions

### One New Owner

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

### Multiple New Owners

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

## Fulfillments

### One Current Owner

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
