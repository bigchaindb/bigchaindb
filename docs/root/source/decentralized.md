# How BigchainDB is Decentralized

Decentralization means that no one owns or controls everything, and there is no single point of failure.

Ideally, each node in a BigchainDB cluster is owned and controlled by a different person or organization. Even if the cluster lives within one organization, it's still preferable to have each node controlled by a different person or subdivision.

We use the phrase "BigchainDB federation" (or just "federation") to refer to the set of people and/or organizations who run the nodes of a BigchainDB cluster. A federation requires some form of governance to make decisions such as membership and policies. The exact details of the governance process are determined by each federation, but it can be very decentralized (e.g. purely vote-based, where each node gets a vote, and there are no special leadership roles).

The actual data is decentralized in that it doesn’t all get stored in one place. Each federation node stores the primary of one shard and replicas of some other shards. (A shard is a subset of the total set of documents.) Sharding and replication are handled by RethinkDB.

Every node has its own locally-stored list of the public keys of other federation members: the so-called keyring. There's no centrally-stored or centrally-shared keyring.

A federation can increase its decentralization (and its resilience) by increasing its jurisdictional diversity, geographic diversity, and other kinds of diversity. This idea is expanded upon in [the section on node diversity](diversity.html).

There’s no node that has a long-term special position in the federation. All nodes run the same software and perform the same duties.

RethinkDB has an “admin” user which can’t be deleted and which can make big changes to the database, such as dropping a table. Right now, that’s a big security vulnerability, but we have plans to mitigate it by:
1. Locking down the admin user as much as possible.
2. Having all nodes inspect RethinkDB admin-type requests before acting on them. Requests can be checked against an evolving whitelist of allowed actions (voted on by federation nodes).

It’s worth noting that the RethinkDB admin user can’t transfer assets, even today. The only way to create a valid transfer transaction is to fulfill the current (crypto) conditions on the asset, and the admin user can’t do that because the admin user doesn’t have the necessary private keys (or preimages, in the case of hashlock conditions). They’re not stored in the database.
