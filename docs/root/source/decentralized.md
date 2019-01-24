<!---
Copyright BigchainDB GmbH and BigchainDB contributors
SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
Code is Apache-2.0 and docs are CC-BY-4.0
--->

# How BigchainDB is Decentralized

Decentralization means that no one owns or controls everything, and there is no single point of failure.

Ideally, each node in a BigchainDB network is owned and controlled by a different person or organization. Even if the network lives within one organization, it's still preferable to have each node controlled by a different person or subdivision.

We use the phrase "BigchainDB consortium" (or just "consortium") to refer to the set of people and/or organizations who run the nodes of a BigchainDB network. A consortium requires some form of governance to make decisions such as membership and policies. The exact details of the governance process are determined by each consortium, but it can be very decentralized.

A consortium can increase its decentralization (and its resilience) by increasing its jurisdictional diversity, geographic diversity, and other kinds of diversity. This idea is expanded upon in [the section on node diversity](diversity).

There’s no node that has a long-term special position in the BigchainDB network. All nodes run the same software and perform the same duties.

If someone has (or gets) admin access to a node, they can mess with that node (e.g. change or delete data stored on that node), but those changes should remain isolated to that node. The BigchainDB network can only be compromised if more than one third of the nodes get compromised. See the [Tendermint documentation](https://tendermint.com/docs/introduction/introduction.html) for more details.

It’s worth noting that not even the admin or superuser of a node can transfer assets. The only way to create a valid transfer transaction is to fulfill the current crypto-conditions on the asset, and the admin/superuser can’t do that because the admin user doesn’t have the necessary information (e.g. private keys).
