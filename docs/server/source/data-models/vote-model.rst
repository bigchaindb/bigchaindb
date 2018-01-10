The Vote Model
==============

A vote is a JSON object with a particular schema,
as outlined in this page.
A vote must contain the following JSON keys
(also called names or fields):

.. code-block:: json

    {
        "node_pubkey": "<The public key of the voting node>",
        "vote": {
            "voting_for_block": "<ID of the block the node is voting on>",
            "previous_block": "<ID of the block previous to the block being voted on>",
            "is_block_valid": "<true OR false>",
            "invalid_reason": null,
            "timestamp": "<Vote-creation timestamp>"
        },
        "signature": "<Signature of inner vote object>"
    }

.. note::
   
   Votes have no ID (or ``"id"``), as far as users are concerned.
   The backend database may use one internally,
   but it's of no concern to users and it's never reported to them via APIs.


The JSON Keys in a Vote
-----------------------

**node_pubkey**

The public key of the node which cast this vote.
It's a string.
For more information about public keys,
see the `IPDB Transaction Spec <https://github.com/ipdb/ipdb-tx-spec>`_
section about cryptographic keys and signatures.


**vote.voting_for_block**

The block ID that this vote is for.
It's a string.
For more information about block IDs,
see the page about :ref:`blocks <The Block Model>`.


**vote.previous_block**

The block ID of the block "before" the block that this vote is for,
according to the node which cast this vote.
It's a string.
(It's possible for different nodes to see different block orders.)
For more information about block IDs,
see the page about :ref:`blocks <The Block Model>`.


**vote.is_block_valid**

``true`` if the node which cast this vote considered the block in question to be valid,
and ``false`` otherwise.
Note that it's a *boolean* (i.e. ``true`` or ``false``), not a string.


**vote.invalid_reason**

Always ``null``, that is, it's not being used.
It may be used or dropped in a future version.
See `bigchaindb/bigchaindb issue #217
<https://github.com/bigchaindb/bigchaindb/issues/217>`_ on GitHub.


**vote.timestamp**

The `Unix time <https://en.wikipedia.org/wiki/Unix_time>`_
when the vote was created, according to the node which created it.
It's a string representation of an integer.


**signature**

The cryptographic signature of the inner ``vote``
by the node that created the vote
(i.e. the node with public key ``node_pubkey``).
To compute that:

#. Construct an :term:`associative array` ``d`` containing the contents of the inner ``vote``
   (i.e. ``vote.voting_for_block``, ``vote.previous_block``, ``vote.is_block_valid``,
   ``vote.invalid_reason``, ``vote.timestamp``, and their values).
#. Compute ``signature = sig_of_aa(d, private_key)``, where ``private_key``
   is the node's private key (i.e. ``node_pubkey`` and ``private_key`` are a key pair).
   There's pseudocode for the ``sig_of_aa()`` function
   on the `IPDB Transaction Spec <https://github.com/ipdb/ipdb-tx-spec>`_
   section about cryptographic keys and signatures.

The Vote Schema
---------------

BigchainDB checks all votes (JSON documents) against a formal schema
defined in a :ref:`JSON Schema file named vote.yaml <The Vote Schema File>`.


An Example Vote
---------------

.. code-block:: json

    {
        "node_pubkey": "3ZCsVWPAhPTqHx9wZVxp9Se54pcNeeM5mQvnozDWyDR9",
        "vote": {
            "voting_for_block": "11c3a3fcc9efa4fc4332a0849fc39b58e403ff37794a7d1fdfb9e7703a94a274",
            "previous_block": "3dd1441018b782a50607dc4c7f83a0f0a23eb257f4b6a8d99330dfff41271e0d",
            "is_block_valid": true,
            "invalid_reason": null,
            "timestamp": "1509977988"
        },
        "signature": "3tW2EBVgxaZTE6nixVd9QEQf1vUxqPmQaNAMdCHc7zHik5KEosdkwScGYt4VhiHDTB6BCxTUzmqu3P7oP93tRWfj"
    }
