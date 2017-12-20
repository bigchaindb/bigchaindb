# Production Node Assumptions

Be sure you know the key BigchainDB terminology:

* [BigchainDB node, BigchainDB cluster and BigchainDB consortium](https://docs.bigchaindb.com/en/latest/terminology.html)
* [dev/test node, bare-bones node and production node](../introduction.html)

We make some assumptions about production nodes:

1. Production nodes use MongoDB (not RethinkDB, PostgreSQL, Couchbase or whatever).
1. Each production node is set up and managed by an experienced professional system administrator or a team of them.
1. Each production node in a cluster is managed by a different person or team.

We don't provide a detailed cookbook explaining how to secure a server, or other things that a sysadmin should know. We do provide some templates, but those are just starting points.
