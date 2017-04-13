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
        "voters": ["<list of public keys of all nodes in the cluster>"]
      },
      "signature": "<signature of block>"
    }


- ``id``: The :ref:`hash <Hashes>` of the serialized inner ``block`` (i.e. the ``timestamp``, ``transactions``, ``node_pubkey``, and ``voters``). It's used as a unique index in the database backend (e.g. RethinkDB or MongoDB).

- ``block``:
    - ``timestamp``: The Unix time when the block was created. It's provided by the node that created the block.
    - ``transactions``: A list of the transactions included in the block.
    - ``node_pubkey``: The public key of the node that created the block.
    - ``voters``: A list of the public keys of all cluster nodes at the time the block was created.
      It's the list of nodes which can cast a vote on this block.
      This list can change from block to block, as nodes join and leave the cluster.

- ``signature``: :ref:`Cryptographic signature <Signature Algorithm and Keys>` of the block by the node that created the block (i.e. the node with public key ``node_pubkey``). To generate the signature, the node signs the serialized inner ``block`` (the same thing that was hashed to determine the ``id``) using the private key corresponding to ``node_pubkey``.


Working with Blocks
-------------------

There's a **Block** class for creating and working with Block objects; look in `/bigchaindb/models.py <https://github.com/bigchaindb/bigchaindb/blob/master/bigchaindb/models.py>`_. (The link is to the latest version on the master branch on GitHub.)
