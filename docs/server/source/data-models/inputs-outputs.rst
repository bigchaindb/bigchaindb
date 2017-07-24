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
       "fulfillment": "<String that fulfills the condition in the output being spent>",
       "fulfills": {
           "output_index": "<Index of the output being spent (an integer)>",
           "transaction_id": "<ID of the transaction containing the output being spent>"
       }
   }

You can think of the ``fulfills`` object as a pointer to an output on another transaction: the output that this input is spending/transferring.
A CREATE transaction should have exactly one input. That input can contain one or more ``owners_before``, a ``fulfillment`` (with one signature from each of the owners-before), and the value of ``fulfills`` should be ``null``). A TRANSFER transaction should have at least one input, and the value of ``fulfills`` should not be ``null``.
See the reference on :ref:`inputs <Input>` for more description about the meaning of each field.

The ``fulfillment`` string fulfills the condition in the output that is being spent (transferred).
To calculate it:

1. Determine the fulfillment as per the `Crypto-Conditions spec (version 02) <https://tools.ietf.org/html/draft-thomas-crypto-conditions-02>`_.
2. Encode the fulfillment using the `ASN.1 Distinguished Encoding Rules (DER) <http://www.itu.int/ITU-T/recommendations/rec.aspx?rec=12483&lang=en>`_.
3. Encode the resulting bytes using "base64url" (*not* typical base64) as per `RFC 4648, Section 5 <https://tools.ietf.org/html/rfc4648#section-5>`_.

To do those calculations, you can use one of the
:ref:`BigchainDB drivers or transaction-builders <Drivers & Tools>`,
or use a low-level crypto-conditions library as illustrated
in the page about `Handcrafting Transactions <https://docs.bigchaindb.com/projects/py-driver/en/latest/handcraft.html>`_.
A ``fulfillment`` string should look something like:

.. code::

   "pGSAIDgbT-nnN57wgI4Cx17gFHv3UB_pIeAzwZCk10rAjs9bgUDxyNnXMl-5PFgSIOrN7br2Tz59MiWe2XY0zlC7LcN52PKhpmdRtcr7GR1PXuTfQ9dE3vGhv7LHn6QqDD6qYHYM"


Outputs
-------

An output has the following structure:

.. code-block:: json

   {
       "condition": {"<Condition object>"},
       "public_keys": ["<List of all public keys associated with the condition object>"],
       "amount": "<Number of shares of the asset (an integer in a string)>"
   }

The :ref:`page about conditions <Conditions>` explains the contents of a ``condition``.

The list of ``public_keys`` is always the "owners" of the asset at the time the transaction completed, but before the next transaction started.
See the reference on :ref:`outputs <Output>` for more description about the meaning of each field.

Note that ``amount`` must be a string (e.g. ``"7"``).
In a TRANSFER transaction, the sum of the output amounts must be the same as the sum of the outputs that it transfers (i.e. the sum of the input amounts). For example, if a TRANSFER transaction has two outputs, one with ``"amount": "2"`` and one with ``"amount": "3"``, then the sum of the outputs is 5 and so the sum of the outputs-being-transferred must also be 5.


.. note::

    The BigchainDB documentation and code talks about control of an asset in terms of "owners" and "ownership." The language is chosen to represent the most common use cases, but in some more complex scenarios, it may not be accurate to say that the output is owned by the controllers of those public keys—it would only be correct to say that those public keys are associated with the ability to fulfill the conditions on the output. Also, depending on the use case, the entity controlling an output via a private key may not be the legal owner of the asset in the corresponding legal domain. However, since we aim to use language that is simple to understand and covers the majority of use cases, we talk in terms of "owners" of an output that have the ability to "spend" that output.
