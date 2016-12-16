Inputs and Outputs
==================

BigchainDB is modelled around *assets*, and *inputs* and *outputs* are the mechanism by which control of an asset is transferred.

Amounts of an asset are encoded in the outputs of a transaction, and each output may be spent separately. In order to spend an output, it's `conditions` must be met, by an `input` that provides corresponding `fulfillments`. Each output may be spent exactly once, by a single input.

.. note::

    This document (and various places in the BigchainDB documentation and code) talks about control of an asset in terms of *owners* and *ownership*. The language is chosen to represent the most common use cases, but in some more complex scenarios, it is not accurate to say that the output is owned by the controllers of those public keys, only that those are the public keys associated with the ability to fulfill the output. Also, depending on the use case, the entity controlling an output via a private key may not be the legal owner of the asset in the corresponding legal domain. However, since we aim to use language that is simple to understand and covers the majority of use cases, we talk in terms of *owners* of an output that have the ability to *spend* that output.

In the most basic case, an output may define a **simple signature condition**, which gives control of the output to the entity controlling a corresponding private key.

A more complex condition can be composed by using n of the above conditions as inputs to an m-of-n threshold condition (a logic gate which outputs TRUE iff m or more inputs are TRUE). If there are n inputs to a threshold condition:
* 1-of-n is the same as a logical OR of all the inputs
* n-of-n is the same as a logical AND of all the inputs

For example, one could create a condition requiring m (of n) signatures before their asset can be transferred.

One can also put different weights on the inputs to threshold condition, along with a threshold that the weighted-sum-of-inputs must pass for the output to be TRUE. Weights could be used, for example, to express the number of units of an asset that someone controls.

The (single) output of a threshold condition can be used as one of the inputs of other threshold conditions. This means that one can combine threshold conditions to build complex logical expressions, e.g. (x OR y) AND (u OR v).

Aside: In BigchainDB, the output of an m-of-n threshold condition can be inverted on the way out, so an output that would have been TRUE would get changed to FALSE (and vice versa). This enables the creation of NOT, NOR and NAND gates. At the time of writing, this “inverted threshold condition” is BigchainDB-specific (i.e. not part of the Interledger specs). It should only be used in combination with a timeout condition.

When one creates a condition, one can calculate its fulfillment length (e.g. 96). The more complex the condition, the larger its fulfillment length will be. A BigchainDB federation can put an upper limit on the allowed fulfillment length, as a way of capping the complexity of conditions (and the computing time required to validate them).

If someone tries to make a condition where the output of a threshold condition feeds into the input of another “earlier” threshold condition (i.e. in a closed logical circuit), then their computer will take forever to calculate the (infinite) “condition URI”, at least in theory. In practice, their computer will run out of memory or their client software will timeout after a while.

Aside: In what follows, the list of `public_keys` (in a condition) is always who controlled the asset at the time the transaction completed, but before the next transaction started. The list of `owners_before` (in an input) is always equal to the list of `public_keys` in that asset's previous transaction.

Outputs
-------

One New Owner
`````````````

If there is only one *new owner*, the output will contain a simple signature condition (i.e. only one signature is required).

.. code-block:: json

    {
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
        "public_keys": ["<new owner public key>"],
        "amount": "<int>"
    }


See the reference on :ref:`outputs <Output>` for descriptions of the meaning of each field.

Multiple New Owners
```````````````````

If there are multiple *new owners*, they can create a ThresholdCondition requiring a signature from each of them in order
to spend the asset. For example:

.. code-block:: json

    {
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
            "public_keys": [
                "owner 1 public key>",
                "owner 2 public key>"
            ]
    }


- `subfulfillments`: a list of fulfillments
    - `weight`: integer weight for each subfulfillment's contribution to the threshold
- `threshold`: threshold to reach for the subfulfillments to reach a valid fulfillment 

The `weight`s and `threshold` could be adjusted. For example, if the `threshold` was changed to 1 above, then only one of the new owners would have to provide a signature to spend the asset.

Inputs
------

One Current Owner
`````````````````

If there is only one *current owner*, the fulfillment will be a simple signature fulfillment (i.e. containing just one signature).

.. code-block:: json

    {
        "owners_before": ["<public key of the owner before the transaction happened>"],
        "fulfillment": "cf:4:RxFzIE679tFBk8zwEgizhmTuciAylvTUwy6EL6ehddHFJOhK5F4IjwQ1xLu2oQK9iyRCZJdfWAefZVjTt3DeG5j2exqxpGliOPYseNkRAWEakqJ_UrCwgnj92dnFRAEE",
        "fulfills": {
            "output": 0,
            "txid": "11b3e7d893cc5fdfcf1a1706809c7def290a3b10b0bef6525d10b024649c42d3"
        }
    }


See the reference on :ref:`inputs <Input>` for descriptions of the meaning of each field.
