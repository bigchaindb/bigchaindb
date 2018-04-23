Querying BigchainDB
===================

A node operator can use the full power of MongoDB's query engine to search and query all stored data, including all transactions, assets and metadata.
The node operator can decide for themselves how much of that query power they expose to external users.

How to Query
------------

A BigchainDB node operator has full access to their local MongoDB instance, so they can use any of MongoDB's APIs for running queries, including:

- `the mongo Shell <https://docs.mongodb.com/manual/mongo/>`_,
- one of `the MongoDB drivers <https://docs.mongodb.com/ecosystem/drivers/>`_, such as `PyMongo <https://api.mongodb.com/python/current/>`_, or
- a third-party tool or driver for doing MongoDB queries, such as RazorSQL.

What Can be Queried?
--------------------

BigchainDB Server creates several `MongoDB collections <https://docs.mongodb.com/manual/core/databases-and-collections/>`_ in the node's local MongoDB database.
You can see the list of collections by looking at the ``create_tables`` method in the BigchainDB Server file ``bigchaindb/backend/localmongodb/schema.py``. The most interesting collections are:

- transactions
- assets
- metadata
- blocks

We don't detail what's in each collection here, but the collection names are fairly self-explanatory. You can explore their contents using MongoDB queries. A couple of things worth noting are:

1. The transactions collection doesn't include any ``asset.data`` or ``metadata`` values (JSON documents). Those are all removed and stored separately in the assets and metadata collections, respectively.
2. The JSON documents stored in the blocks collection are *not* `Tendermint blocks <https://github.com/tendermint/tendermint/blob/master/types/block.go>`_, they are `BigchainDB blocks <https://docs.bigchaindb.com/projects/server/en/latest/data-models/block-model.html>`_.
3. Votes aren't stored in any MongoDB collection, currently. They are all handled and stored by Tendermint in its own (LevelDB) database.

What a Node Operator Can Expose to External Users
-------------------------------------------------

Each node operator can decide how they let external users get information from their local MongoDB database. They could expose:

- their local MonogoDB database itself to queries from external users, maybe as a MongoDB user with a role that has limited privileges, e.g. read-only.
- a limited HTTP API, allowing a restricted set of predefined queries, such as `the HTTP API provided by BigchainDB Server <http://bigchaindb.com/http-api>`_, or a custom HTTP API implemented using Django, Express, Ruby on Rails, or ASP.NET.
- some other API, such as a GraphQL API. They could do that using custom code or code from a third party.

Each node operator can expose a different level or type of access to their local MongoDB database.
For example, one node operator might decide to specialize in offering optimized `geospatial queries <https://docs.mongodb.com/manual/reference/operator/query-geospatial/>`_.

Security Considerations
-----------------------

In BigchainDB version 1.3.0 and earlier, there was one logical MongoDB database, so exposing that database to external users was very risky, and was not recommended.
"Drop database" would delete that one shared MongoDB database.

In BigchainDB version 2.0.0 and later, each node has its own isolated local MongoDB database.
Inter-node communications are done using Tendermint protocols, not MongoDB protocols, as illustrated in Figure 1 below.
If a node's local MongoDB database gets compromised, none of the other MongoDB databases (in the other nodes) will be affected.

.. figure:: _static/schemaDB.png
   :alt: Diagram of a four-node BigchainDB 2.0 network
   :align: center
   
   Figure 1: A Four-Node BigchainDB 2.0 Network

.. raw:: html

   <br>
   <br>
   <br>

Performance and Cost Considerations
-----------------------------------

Query processing can be quite resource-intensive, so it's a good idea to have MongoDB running in a separate machine from those running BigchainDB Server and Tendermint Core.

A node operator might want to measure the resources used by a query, so they can charge whoever requested the query accordingly.

Some queries can take too long or use too many resources. A node operator should put upper bounds on the resources that a query can use, and halt (or prevent) any query that goes over.

To make MongoDB queries more efficient, one can create `indexes <https://docs.mongodb.com/manual/indexes/>`_. Those indexes might be created by the node operator or by some external users (if the node operator allows that). It's worth noting that indexes aren't free: whenever new data is appended to a collection, the corresponding indexes must be updated. The node operator might want to pass those costs on to whoever created the index. Moreover, in MongoDB, `a single collection can have no more than 64 indexes <https://docs.mongodb.com/manual/reference/limits/#Number-of-Indexes-per-Collection>`_.

One can create a follower node: a node with Tendermint voting power 0. It would still have a copy of all the data, so it could be used as read-only node. A follower node could offer specialized queries as a service without affecting the workload on the voting validators (which can also write). There could even be followers of followers.
