Conditions
==========

At a high level, a condition is like a lock on an output.
If can you satisfy the condition, you can unlock the output and transfer/spend it.
BigchainDB Server supports a subset of the ILP Crypto-Conditions
(`version 02 of Crypto-Conditions <https://tools.ietf.org/html/draft-thomas-crypto-conditions-02>`_).

A condition object can be quite elaborate,
with many nested levels,
but the simplest case is actually quite simple.
Here's an example signature condition:

.. code-block:: json

   {
       "details": {
           "type": "ed25519-sha-256",
           "public_key": "HFp773FH21sPFrn4y8wX3Ddrkzhqy4La4cQLfePT2vz7"
       },
       "uri": "ni:///sha-256;at0MY6Ye8yvidsgL9FrnKmsVzX0XrNNXFmuAPF4bQeU?fpt=ed25519-sha-256&cost=131072"
   }

If someone wants to spend the output where this condition is found, then they must create a TRANSFER transaction with an input that fulfills it (this condition). Because it's a ed25519-sha-256 signature condition, that means they must sign the TRANSFER transaction with the private key corresponding to the public key HFp773…


Supported Crypto-Conditions
---------------------------

BigchainDB Server v1.0 supports two of the Crypto-Conditions:

1. ED25519-SHA-256 signature conditions
2. THRESHOLD-SHA-256 threshold conditions

We saw an example signature condition above.
For more information about how BigchainDB handles keys and signatures,
see the page titled :ref:`Signature Algorithm and Keys`.

A more complex condition can be composed by using n signature conditions as inputs to an m-of-n threshold condition: a logic gate which outputs TRUE if and only if m or more inputs are TRUE. If there are n inputs to a threshold condition:

* 1-of-n is the same as a logical OR of all the inputs
* n-of-n is the same as a logical AND of all the inputs

For example, you could create a condition requiring m (of n) signatures.
Here's an example 2-of-2 condition:

.. code-block:: json

   {
       "details": {
           "type": "threshold-sha-256",
           "threshold": 2,
           "subconditions": [
               {
                   "public_key": "5ycPMinRx7D7e6wYXLNLa3TCtQrMQfjkap4ih7JVJy3h",
                   "type": "ed25519-sha-256"
               },
               {
                   "public_key": "9RSas2uCxR5sx1rJoUgcd2PB3tBK7KXuCHbUMbnH3X1M",
                   "type": "ed25519-sha-256"
                }
            ]       
        },
        "uri": "ni:///sha-256;zr5oThl2kk6613WKGFDg-JGu00Fv88nXcDcp6Cyr0Vw?fpt=threshold-sha-256&cost=264192&subtypes=ed25519-sha-256"
   }

The (single) output of a threshold condition can be used as one of the inputs to another threshold condition. That means you can combine threshold conditions to build complex expressions such as ``(x OR y) AND (2 of {a, b, c})``.

.. image:: /_static/Conditions_Circuit_Diagram.png

When you create a condition, you can calculate its
`cost <https://tools.ietf.org/html/draft-thomas-crypto-conditions-02#section-7.2.2>`_,
an estimate of the resources that would be required to validate the fulfillment.
For example, the cost of one signature condition is 131072.
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


Constructing a Condition
------------------------

The above examples should make it clear how to construct
a condition object, but they didn't say how to generate the ``uri``.
If you want to generate a correct condition URI,
then you should consult the Crypto-Conditions spec
or use one of the existing Crypto-Conditions packages/libraries
(which are used by the BigchainDB Drivers).

* `Crypto-Conditions Spec (Version 02) <https://tools.ietf.org/html/draft-thomas-crypto-conditions-02>`_
* BigchainDB :ref:`Drivers & Tools`

The `Handcrafting Transactions <https://docs.bigchaindb.com/projects/py-driver/en/latest/handcraft.html>`_
page may also be of interest.
