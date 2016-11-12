The Transaction Model
=====================

Every transaction has the following JSON structure:

.. code-block:: json

    {
      "id": "<hash of transaction, excluding signatures (see explanation)>",
      "version": "<version number of the transaction model>",
      "transaction": {
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


Here's some explanation of the contents of a transaction:

- ``id``: The hash of everything else in the transaction 
  (but with all fulfillment URIs replaced by ``null``).
  The ``id`` is also the database primary key.
- ``version``: Version number of the transaction model, 
  so that software can support different transaction models.

Inside ``transaction``:

- ``fulfillments``: List of fulfillments. Each fulfillment contains a pointer to an unfulfilled condition and information that fulfills that condition. See the page about :doc:`Crypto-Conditions and Fulfillments <crypto-conditions>`.
- ``conditions``: List of conditions. Each condition is a crypto-condition that must be satisfied to transfer the asset. See the page about :doc:`Crypto-Conditions and Fulfillments <crypto-conditions>`.
- ``operation``: String representation of the operation being performed (currently either "CREATE", "TRANSFER" or "GENESIS"). It determines how the transaction should be validated.
- ``timestamp``: The Unix time when the transaction was created. It's provided by the client. See the page about `timestamps in BigchainDB <https://docs.bigchaindb.com/en/latest/timestamps.html>`_.
- ``asset``: Definition of the digital asset. See the :doc:`digital asset model <asset-model>`.
- ``metadata``:
    - ``id``: UUID version 4 (random) converted to a string of hex digits in standard form.
    - ``data``: Can be any JSON document. It may be empty in the case of a transfer transaction.

Later, when we get to the models for the block and the vote, we'll see that both include a signature (from the node which created it). You may wonder why transactions don't have signatures... The answer is that they do! They're just hidden inside the ``fulfillment`` string of each fulfillment. What gets signed? The same message that gets hashed to compute the overall transaction ``id``.

.. toctree::
   :maxdepth: 1

   The Transaction Model <self>
   asset-model
   crypto-conditions
   