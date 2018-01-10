The Block Model
===============

A block is a JSON object with a particular schema,
as outlined in this page.
A block must contain the following JSON keys
(also called names or fields):

.. code-block:: json

    {
      "id": "<ID of the block>",
      "block": {
        "timestamp": "<Block-creation timestamp>",
        "transactions": ["<List of transactions>"],
        "node_pubkey": "<Public key of the node which created the block>",
        "voters": ["<List of public keys of all nodes in the cluster>"]
      },
      "signature": "<Signature of inner block object>"
    }


The JSON Keys in a Block
------------------------

**id**

The transaction ID and also the SHA3-256 hash
of the inner ``block`` object, loosely speaking.
It's a string.
To compute it, 1) construct an :term:`associative array` ``d`` containing
``block.timestamp``, ``block.transactions``, ``block.node_pubkey``,
``block.voters``, and their values. 2) compute ``id = hash_of_aa(d)``.
There's pseudocode for the ``hash_of_aa()`` function
in the `IPDB Transaction Spec <https://github.com/ipdb/ipdb-tx-spec>`_
section about cryptographic hashes.
The result (``id``) is a string: the block ID.
An example is ``"b60adf655932bf47ef58c0bfb2dd276d4795b94346b36cbb477e10d7eb02cea8"``


**block.timestamp**

The `Unix time <https://en.wikipedia.org/wiki/Unix_time>`_
when the block was created, according to the node which created it.
It's a string representation of an integer.
An example is ``"1507294217"``.


**block.transactions**

A list of the :ref:`transactions <The Transaction Model>` included in the block.
(Each transaction is a JSON object.)


**block.node_pubkey**

The public key of the node that created the block.
It's a string.
See the `IPDB Transaction Spec <https://github.com/ipdb/ipdb-tx-spec>`_
section about cryptographic keys & signatures.


**block.voters**

A list of the public keys of all cluster nodes at the time the block was created.
It's a list of strings.
This list can change from block to block, as nodes join and leave the cluster.


**signature**

The cryptographic signature of the inner ``block``
by the node that created the block
(i.e. the node with public key ``node_pubkey``).
To compute that:

#. Construct an :term:`associative array` ``d`` containing the contents
   of the inner ``block``
   (i.e. ``block.timestamp``, ``block.transactions``, ``block.node_pubkey``,
   ``block.voters``, and their values).
#. Compute ``signature = sig_of_aa(d, private_key)``,
   where ``private_key`` is the node's private key
   (i.e. ``node_pubkey`` and ``private_key`` are a key pair). There's pseudocode
   for the ``sig_of_aa()`` function
   on the `IPDB Transaction Spec <https://github.com/ipdb/ipdb-tx-spec>`_
   section about cryptographic keys and signatures.

.. note::

   The ``d_bytes`` computed when computing the block ID will be the *same* as the ``d_bytes`` computed when computing the block signature. This can be used to avoid redundant calculations.
