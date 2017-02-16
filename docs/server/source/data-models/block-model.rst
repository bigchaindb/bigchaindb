The Block Model
===============

A block has the following structure:

.. code-block:: json

    {
      "id": "<hash of block>",
      "block": {
        "timestamp": "<block-creation timestamp>",
        "transactions": ["<list of transactions>"],
        "node_pubkey": "<public key of the node creating the block>",
        "voters": ["<list of federation nodes public keys>"]
      },
      "signature": "<signature of block>"
    }


- ``id``: The :ref:`hash <Hashes>` of the serialized inner ``block`` (i.e. the ``timestamp``, ``transactions``, ``node_pubkey``, and ``voters``). It's used as a unique index in the database backend (e.g. RethinkDB or MongoDB).

- ``block``:
    - ``timestamp``: The Unix time when the block was created. It's provided by the node that created the block.
    - ``transactions``: A list of the transactions included in the block.
    - ``node_pubkey``: The public key of the node that created the block.
    - ``voters``: A list of the public keys of federation nodes at the time the block was created.
      It's the list of federation nodes which can cast a vote on this block.
      This list can change from block to block, as nodes join and leave the federation.

- ``signature``: :ref:`Cryptographic signature <Signature Algorithm and Keys>` of the block by the node that created the block. To generate the signature, the node builds a dict including the ``id``, the inner ``block`` & the ``signature`` (with a value of ``None``), it serializes that dict, and then signs *that* with its private key.


Working with Blocks
-------------------

There's a **Block** class for creating and working with Block objects; look in `/bigchaindb/models.py <https://github.com/bigchaindb/bigchaindb/blob/master/bigchaindb/models.py>`_. (The link is to the latest version on the master branch on GitHub.)
