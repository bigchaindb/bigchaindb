Example Apps
============

.. warning::

   There are some example BigchainDB apps (i.e. apps which use BigchainDB) in the GitHub repository named `bigchaindb-examples <https://github.com/bigchaindb/bigchaindb-examples>`_. They were created before there was much of an HTTP API, so instead of communicating with a BigchainDB node via the HTTP API, they communicate directly with the node using the BigchainDB Python server API and the RethinkDB Python Driver. That's not how a real production app would work. The HTTP API is getting better, and we recommend using it to communicate with BigchainDB nodes.

   Moreover, because of changes to the BigchainDB Server code, some of the examples in the bigchaindb-examples repo might not work anymore, or they might not work as expected.

   In the future, we hope to create a set of examples using the HTTP API (or wrappers of it, such as the Python Driver API).
