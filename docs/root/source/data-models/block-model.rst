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


- ``id``: The hash of the serialized ``block`` (i.e. the ``timestamp``, ``transactions``, ``node_pubkey``, and ``voters``). This is also a database primary key; that's how we ensure that all blocks are unique.

- ``block``:
    - ``timestamp``: The Unix time when the block was created. It's provided by the node that created the block.
    - ``transactions``: A list of the transactions included in the block.
    - ``node_pubkey``: The public key of the node that created the block.
    - ``voters``: A list of the public keys of federation nodes at the time the block was created.
      It's the list of federation nodes which can cast a vote on this block.
      This list can change from block to block, as nodes join and leave the federation.

- ``signature``: Cryptographic signature of the block by the node that created the block. (To create the signature, the node serializes the block contents and signs it with its private key.)


Working with Blocks
-------------------

There's a **Block** class for creating and working with Block objects; look in `/bigchaindb/models.py <https://github.com/bigchaindb/bigchaindb/blob/master/bigchaindb/models.py>`_. (The link is to the latest version on the master branch on GitHub.)
