==================
Transaction Schema
==================

* `Transaction`_

* `Transaction Body`_

* Condition_

* Fulfillment_

* Asset_

* Metadata_

* Timestamp_

.. raw:: html

    <style>
    #transaction-schema h2 {
         border-top: solid 3px #6ab0de;
         background-color: #e7f2fa;
         padding: 5px;
    }
    #transaction-schema h3 {
         background: #f0f0f0;
         border-left: solid 3px #ccc;
         font-weight: bold;
         padding: 6px;
         font-size: 100%;
         font-family: monospace;
    }
    </style>

Transaction
-----------

This is the outer transaction wrapper. It contains the ID, version and the body of the transaction, which is also called `transaction`.


transaction.id
^^^^^^^^^^^^^^

**type:** string

A sha3 digest of the transaction. The ID is calculated by removing all
derived hashes and signatures from the transaction, serializing it to
JSON with keys in sorted order and then hashing the resulting string
with sha3.



transaction.transaction
^^^^^^^^^^^^^^^^^^^^^^^

**type:** object

Body of the transaction.



transaction.version
^^^^^^^^^^^^^^^^^^^

**type:** integer

Transaction version identifier.





Transaction Body
----------------

Body of the transaction.


transaction.operation
^^^^^^^^^^^^^^^^^^^^^

**type:** string

Type of the transaction:

A `CREATE` transaction creates an asset in BigchainDB. This
transaction has outputs (conditions) but no inputs (fulfillments),
so a dummy fulfillment is used.

A `TRANSFER` transaction transfers ownership of an asset, by providing
fulfillments to conditions of earlier transactions.

A `GENESIS` transaction is a special case transaction used as the
sole member of the first block in a BigchainDB ledger.



transaction.asset
^^^^^^^^^^^^^^^^^

**type:** object

Description of the asset being transacted. In the case of a `TRANSFER`
transaction, this field contains only the ID of asset. In the case
of a `CREATE` transaction, this field may contain properties:



transaction.fulfillments
^^^^^^^^^^^^^^^^^^^^^^^^

**type:** array (object)

Array of the fulfillments (inputs) of a transaction.

See: fulfillment_.



transaction.conditions
^^^^^^^^^^^^^^^^^^^^^^

**type:** array (object)

Array of conditions (outputs) provided by this transaction.



transaction.metadata
^^^^^^^^^^^^^^^^^^^^

**type:** object or NULL

User provided transaction metadata. This field may be `null` or may
contain any valid JSON payload provided by the user.



transaction.timestamp
^^^^^^^^^^^^^^^^^^^^^

**type:** string

User provided timestamp of the transaction.





Condition
----------

An output of a transaction. A condition describes a quantity of an asset
and what conditions must be met in order for it to be fulfilled. See also:
fulfillment_.


conditions.cid
^^^^^^^^^^^^^^

**type:** integer

Index of this transaction's appearance in the `transaction.conditions`_
array. In a transaction with 2 conditions, the `cid`s will be 0 and 1.



conditions.condition
^^^^^^^^^^^^^^^^^^^^

**type:** object

Body of the condition. Has the properties:

- **details**: Cryptographic details of the condition.
- **uri**: Cryptographic URI of the condition. TODO: more better.



conditions.owners_after
^^^^^^^^^^^^^^^^^^^^^^^

**type:** array (string) or NULL

TODO



conditions.amount
^^^^^^^^^^^^^^^^^

**type:** integer

Integral amount of the asset represented by this condition.
In the case of a non divisible asset, this will always be 1.





Fulfillment
-----------

A fulfillment is an input to a transaction, named as such because it fulfills a condition of a previous transaction. In the case of a **CREATE** transaction, a fulfillment may provide no `input`.

fulfillment.fid
^^^^^^^^^^^^^^^

**type:** integer

The offset of the fulfillment within the fulfillents array.



fulfillment.current_owners
^^^^^^^^^^^^^^^^^^^^^^^^^^

**type:** array (string) or NULL

List of public keys of the new owners of the asset.



fulfillment.fulfillment
^^^^^^^^^^^^^^^^^^^^^^^

**type:** string

A standardised *uri* string representing the signed fulfillment".



fulfillment.input
^^^^^^^^^^^^^^^^^

**type:** string or NULL

TODO





Asset
-----

Description of the asset being transacted. In the case of a `TRANSFER`
transaction, this field contains only the ID of asset. In the case
of a `CREATE` transaction, this field may contain properties:


asset.id
^^^^^^^^

**type:** string

A `UUID <https://en.wikipedia.org/wiki/Universally_unique_identifier>`_
of type 4 (random).



asset.divisible
^^^^^^^^^^^^^^^

**type:** boolean

Whether or not the asset has a quantity that may be partially spent.



asset.updatable
^^^^^^^^^^^^^^^

**type:** boolean

TODO



asset.refillable
^^^^^^^^^^^^^^^^

**type:** boolean

TODO



asset.data
^^^^^^^^^^

**type:** object or NULL

User provided metadata associated with the asset. May also be NULL.





Metadata
--------

User provided transaction metadata. This field may be `null` or may
contain any valid JSON payload provided by the user.


metadata.data
^^^^^^^^^^^^^

**type:** object

Freeform object containing user provided asset metadata.



metadata.id
^^^^^^^^^^^

**type:** string

A `UUID <https://en.wikipedia.org/wiki/Universally_unique_identifier>`_
of type 4 (random).




