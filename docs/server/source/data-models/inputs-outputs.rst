Inputs and Outputs
==================

There's a high-level overview of inputs and outputs
in `the root docs page about transaction concepts <https://docs.bigchaindb.com/en/latest/transaction-concepts.html>`_.

BigchainDB is modelled around *assets*, and *inputs* and *outputs* are the mechanism by which control of an asset (or shares of an asset) is transferred.
Amounts of an asset are encoded in the outputs of a transaction, and each output may be spent separately. To spend an output, the output's ``condition`` must be met by an ``input`` that provides a corresponding ``fulfillment``. Each output may be spent at most once, by a single input. Note that any asset associated with an output holding an amount greater than one is considered a divisible asset that may be split up in future transactions.


Inputs
------

An input has the following structure:

.. code-block:: json

   {
       "owners_before": ["<The public_keys list in the output being spent>"],
       "fulfillment": "<Fulfillment URI fulfilling the condition of the output being spent>",
       "fulfills": {
           "output_index": "<Index of the output being spent (an integer)>",
           "transaction_id": "<ID of the transaction containing the output being spent>"
       }
   }

You can think of the ``fulfills`` object as a pointer to an output on another transaction: the output that this input is spending/transferring.
A CREATE transaction should have exactly one input. That input can contain one or more ``owners_before``, a ``fulfillment`` (with one signature from each of the owners-before), and the value of ``fulfills`` should be ``null``). A TRANSFER transaction should have at least one input, and the value of ``fulfills`` should not be ``null``.
See the reference on :ref:`inputs <Input>` for more description about the meaning of each field.

To calculate a fulfillment URI, you can use one of the
:ref:`BigchainDB drivers or transaction-builders <Drivers & Clients>`,
or use a low-level crypto-conditions library as illustrated
in the page about `Handcrafting Transactions <https://docs.bigchaindb.com/projects/py-driver/en/latest/handcraft.html>`_.


Outputs
-------

An output has the following structure:

.. code-block:: json

   {
       "condition": {"<Condition object>"},
       "public_keys": ["<List of all public keys associated with the condition object>"],
       "amount": "<Number of shares of the asset (an integer in a string)>"
   }

The list of ``public_keys`` is always the "owners" of the asset at the time the transaction completed, but before the next transaction started.
See the reference on :ref:`outputs <Output>` for more description about the meaning of each field.

Below is a high-level description of what goes into building a ``condition`` object.
To construct an actual ``condition`` object, you can use one of the
:ref:`BigchainDB drivers or transaction-builders <Drivers & Clients>`,
or use a low-level crypto-conditions library as illustrated
in the page about `Handcrafting Transactions <https://docs.bigchaindb.com/projects/py-driver/en/latest/handcraft.html>`_.


Conditions
----------

At a high level, a condition is like a lock on an output.
If can you satisfy the condition, you can unlock the output and transfer/spend it.
BigchainDB Server v1.0 supports a subset of the ILP Crypto-Conditions
(`version 02 of Crypto-Conditions <https://tools.ietf.org/html/draft-thomas-crypto-conditions-02>`_).

The simplest supported condition is a simple signature condition.
Such a condition could be stated as,
"You can satisfy this condition
if you send me a message and a cryptographic signature of that message,
produced using the private key corresponding to this public key."
The public key is put in the output.
BigchainDB currently only supports ED25519 signatures.

A more complex condition can be composed by using n simple signature conditions as inputs to an m-of-n threshold condition (a logic gate which outputs TRUE if and only if m or more inputs are TRUE). If there are n inputs to a threshold condition:

* 1-of-n is the same as a logical OR of all the inputs
* n-of-n is the same as a logical AND of all the inputs

For example, one could create a condition requiring m (of n) signatures before their asset can be transferred.

The (single) output of a threshold condition can be used as one of the inputs of other threshold conditions. This means that one can combine threshold conditions to build complex logical expressions, e.g. (x OR y) AND (u OR v).

When one creates a condition, one can calculate its
`cost <https://tools.ietf.org/html/draft-thomas-crypto-conditions-02#section-7.2.2>`_,
an estimate of the resources that would be required to validate the fulfillment.
A BigchainDB federation can put an upper limit on the complexity of each
condition, either directly by setting a maximum allowed cost,
or
`indirectly <https://github.com/bigchaindb/bigchaindb/issues/356#issuecomment-288085251>`_
by :ref:`setting a maximum allowed transaction size <Enforcing a Max Transaction Size>`
which would limit
the overall complexity accross all inputs and outputs of a transaction.
Note: At the time of writing, there was no configuration setting
to set a maximum allowed cost,
so the only real option was to
:ref:`set a maximum allowed transaction size <Enforcing a Max Transaction Size>`.


.. note::

    The BigchainDB documentation and code talks about control of an asset in terms of "owners" and "ownership." The language is chosen to represent the most common use cases, but in some more complex scenarios, it may not be accurate to say that the output is owned by the controllers of those public keys—it would only be correct to say that those public keys are associated with the ability to fulfill the conditions on the output. Also, depending on the use case, the entity controlling an output via a private key may not be the legal owner of the asset in the corresponding legal domain. However, since we aim to use language that is simple to understand and covers the majority of use cases, we talk in terms of "owners" of an output that have the ability to "spend" that output.
