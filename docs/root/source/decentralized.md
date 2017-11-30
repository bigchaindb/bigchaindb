# How BigchainDB is Decentralized

Decentralization means that no one owns or controls everything, and there is no single point of failure.

Ideally, each node in a BigchainDB cluster is owned and controlled by a different person or organization. Even if the cluster lives within one organization, it's still preferable to have each node controlled by a different person or subdivision.

We use the phrase "BigchainDB consortium" (or just "consortium") to refer to the set of people and/or organizations who run the nodes of a BigchainDB cluster. A consortium requires some form of governance to make decisions such as membership and policies. The exact details of the governance process are determined by each consortium, but it can be very decentralized (e.g. purely vote-based, where each node gets a vote, and there are no special leadership roles).

If sharding is turned on (i.e. if the number of shards is larger than one), then the actual data is decentralized in that no one node stores all the data.

Every node has its own locally-stored list of the public keys of other consortium members: the so-called keyring. There's no centrally-stored or centrally-shared keyring.

A consortium can increase its decentralization (and its resilience) by increasing its jurisdictional diversity, geographic diversity, and other kinds of diversity. This idea is expanded upon in [the section on node diversity](diversity.html).

There’s no node that has a long-term special position in the cluster. All nodes run the same software and perform the same duties.

If someone has (or gets) admin access to a node, they can mess with that node (e.g. change or delete data stored on that node), but those changes should remain isolated to that node. The BigchainDB cluster can only be compromised if more than one third of the nodes get compromised. See the [Tendermint documentation](https://tendermint.readthedocs.io/projects/tools/en/master/introduction.html) for more details.

It’s worth noting that not even the admin or superuser of a node can transfer assets. The only way to create a valid transfer transaction is to fulfill the current crypto-conditions on the asset, and the admin/superuser can’t do that because the admin user doesn’t have the necessary information (e.g. private keys).
