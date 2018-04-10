Querying BigchainDB
===================

A node operator can use the full power of MongoDB's query engine to search and query all stored data, including all transactions, assets and metadata.
The node operator can decide for themselves how much of that query power they expose to external users. For example:

- They could expose their local MonogoDB database itself to queries from external users (maybe as a MongoDB user with limited permissions).
- They could expose a limited HTTP API, allowing a restricted set of predefined queries, e.g. the HTTP API provided by BigchainDB Server.
- They could expose some other API, such as a GraphQL API. They might do that using custom code or code from a third party.

Each node operator can expose a different level or type of access to their local MongoDB database.
For example, one node operator might decide to specialize in offering optimized `geospatial queries <https://docs.mongodb.com/manual/reference/operator/query-geospatial/>`_.

How to Query
------------

A BigchainDB *node operator* has full access to their local MongoDB instance, so they can use any of MongoDB's APIs for running queries, including:

- `the mongo Shell <https://docs.mongodb.com/manual/mongo/>`_,
- one of `the MongoDB drivers <https://docs.mongodb.com/ecosystem/drivers/>`_, such as `PyMongo <https://api.mongodb.com/python/current/>`_, or
- a third-party tool or driver for doing MongoDB queries.

What Can be Queried?
--------------------

BigchainDB Server creates several `MongoDB collections <https://docs.mongodb.com/manual/core/databases-and-collections/>`_ in the node's local MongoDB database.
You can see the list of collections by looking at the ``create_tables`` method in the BigchainDB Server file ``bigchaindb/backend/localmongodb/schema.py``. The most interesting collections are:

- transactions
- assets
- metadata
- blocks

We don't detail what's in each collection here, but the collection names are fairly self-explanatory. You can explore their contents using MongoDB queries. A couple of things worth noting are:

1. The transactions collection *doesn't* include any ``asset.data`` or ``metadata`` values (JSON documents). Those are all removed and stored separately in the assets and metadata collections, respectively.
2. The JSON documents stored in the blocks collection are *not* `Tendermint blocks <https://github.com/tendermint/tendermint/blob/master/types/block.go>`_, they are `BigchainDB blocks <https://docs.bigchaindb.com/projects/server/en/latest/data-models/block-model.html>`_.

Security Considerations
-----------------------

In BigchainDB version 1.3.0 and earlier, there was one logical MongoDB database, so exposing that database to external users was very risky, and was not recommended.
"Drop database" would delete that one shared MongoDB database.

In BigchainDB version 2.0.0 and later, each node has its own isolated local MongoDB database. Inter-node communications is via Tendermint protocols, not MongoDB protocols. If a node's local MongoDB database gets compromised, none of the other local MongoDB databases are affected.

TODO: Include the new diagram of a four-node network.


Performance Considerations
--------------------------

Indexing

Need to be careful not to overload the server.

Follower nodes with voting power 0 will still have a copy of all the data, so they can be used as read-only nodes.

