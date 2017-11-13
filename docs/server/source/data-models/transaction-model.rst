The Transaction Model
=====================

A transaction has the following structure:

.. code-block:: json

    {
        "id": "<ID of the transaction>",
        "version": "<Transaction schema version number>",
        "inputs": ["<List of inputs>"],
        "outputs": ["<List of outputs>"],
        "operation": "<String>",
        "asset": {"<Asset model; see below>"},
        "metadata": {"<Arbitrary transaction metadata>"}
    }

Here's some explanation of the contents:

- **id**: The ID of the transaction and also the hash of the transaction (loosely speaking). See below for an explanation of how it's computed. It's also the database primary key.

- **version**: The version-number of the transaction schema. As of BigchainDB Server 1.0.0, the only allowed value is ``"1.0"``.

- **inputs**: List of inputs.
  Each input spends/transfers a previous output by satisfying/fulfilling
  the crypto-conditions on that output.
  A CREATE transaction should have exactly one input.
  A TRANSFER transaction should have at least one input (i.e. ≥1).

- **outputs**: List of outputs.
  Each output indicates the crypto-conditions which must be satisfied
  by anyone wishing to spend/transfer that output.
  It also indicates the number of shares of the asset tied to that output.

- **operation**: A string indicating what kind of transaction this is,
  and how it should be validated.
  It can only be ``"CREATE"``, ``"TRANSFER"`` or ``"GENESIS"``
  (but there should only be one transaction whose operation is ``"GENESIS"``:
  the one in the GENESIS block).

- **asset**: A JSON document for the asset associated with the transaction.
  (A transaction can only be associated with one asset.)
  See :ref:`the page about the asset model <The Asset Model>`.

- **metadata**: User-provided transaction metadata.
  It can be any valid JSON document, or ``null``.
  **NOTE:** When using MongoDB for storage, certain restriction apply
  to all (including nested) keys of the ``"data"`` JSON document:
  1) keys (i.e. key names, not values) must **not** begin with the ``$`` character, and
  2) keys must not contain ``.`` or the null character (Unicode code point 0000).

**How the transaction ID is computed.**
1) Build a Python dictionary containing ``version``, ``inputs``, ``outputs``, ``operation``, ``asset``, ``metadata`` and their values, 
2) In each of the inputs, replace the value of each ``fulfillment`` with ``null``,
3) :ref:`Serialize <JSON Serialization>` that dictionary,
4) The transaction ID is just :ref:`the SHA3-256 hash <Hashes>` of the serialized dictionary.

**About signing the transaction.**
Later, when we get to the models for the block and the vote, we'll see that both include a signature (from the node which created it). You may wonder why transactions don't have signatures… The answer is that they do! They're just hidden inside the ``fulfillment`` string of each input. What gets signed (as of version 1.0.0) is everything inside the transaction, including the ``id``, but the value of each ``fulfillment`` is replaced with ``null``.

There are example BigchainDB transactions in
:ref:`the HTTP API documentation <The HTTP Client-Server API>`
and
`the Python Driver documentation <https://docs.bigchaindb.com/projects/py-driver/en/latest/usage.html>`_.
