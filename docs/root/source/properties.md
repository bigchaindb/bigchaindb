<!---
Copyright © 2020 Interplanetary Database Association e.V.,
BigchainDB and IPDB software contributors.
SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
Code is Apache-2.0 and docs are CC-BY-4.0
--->

# Properties of BigchainDB 

### Decentralization

Decentralization means that no one owns or controls everything, and there is no single point of failure.

Ideally, each node in a BigchainDB network is owned and controlled by a different person or organization. Even if the network lives within one organization, it's still preferable to have each node controlled by a different person or subdivision.

We use the phrase "BigchainDB consortium" (or just "consortium") to refer to the set of people and/or organizations who run the nodes of a BigchainDB network. A consortium requires some form of governance to make decisions such as membership and policies. The exact details of the governance process are determined by each consortium, but it can be very decentralized.

A consortium can increase its decentralization (and its resilience) by increasing its jurisdictional diversity, geographic diversity, and other kinds of diversity.

There’s no node that has a long-term special position in the BigchainDB network. All nodes run the same software and perform the same duties.

If someone has (or gets) admin access to a node, they can mess with that node (e.g. change or delete data stored on that node), but those changes should remain isolated to that node. The BigchainDB network can only be compromised if more than one third of the nodes get compromised. See the [Tendermint documentation](https://tendermint.com/docs/introduction/introduction.html) for more details.

It’s worth noting that not even the admin or superuser of a node can transfer assets. The only way to create a valid transfer transaction is to fulfill the current crypto-conditions on the asset, and the admin/superuser can’t do that because the admin user doesn’t have the necessary information (e.g. private keys).

### Byzantine Fault Tolerance

[Tendermint](https://tendermint.com/) is used for consensus and transaction replication,
and Tendermint is [Byzantine Fault Tolerant (BFT)](https://en.wikipedia.org/wiki/Byzantine_fault_tolerance).

### Node Diversity

Steps should be taken to make it difficult for any one actor or event to control or damage “enough” of the nodes. (Because BigchainDB Server uses Tendermint, "enough" is ⅓.) There are many kinds of diversity to consider, listed below. It may be quite difficult to have high diversity of all kinds.

1. **Jurisdictional diversity.** The nodes should be controlled by entities within multiple legal jurisdictions, so that it becomes difficult to use legal means to compel enough of them to do something.
1. **Geographic diversity.** The servers should be physically located at multiple geographic locations, so that it becomes difficult for a natural disaster (such as a flood or earthquake) to damage enough of them to cause problems.
1. **Hosting diversity.** The servers should be hosted by multiple hosting providers (e.g. Amazon Web Services, Microsoft Azure, Digital Ocean, Rackspace), so that it becomes difficult for one hosting provider to influence enough of the nodes.
1. **Diversity in general.** In general, membership diversity (of all kinds) confers many advantages on a consortium. For example, it provides the consortium with a source of various ideas for addressing challenges.

Note: If all the nodes are running the same code, i.e. the same implementation of BigchainDB, then a bug in that code could be used to compromise all of the nodes. Ideally, there would be several different, well-maintained implementations of BigchainDB Server (e.g. one in Python, one in Go, etc.), so that a consortium could also have a diversity of server implementations. Similar remarks can be made about the operating system.

### Immutability

The blockchain community often describes blockchains as “immutable.” If we interpret that word literally, it means that blockchain data is unchangeable or permanent, which is absurd. The data _can_ be changed. For example, a plague might drive humanity extinct; the data would then get corrupted over time due to water damage, thermal noise, and the general increase of entropy.

It’s true that blockchain data is more difficult to change (or delete) than usual. It's more than just "tamper-resistant" (which implies intent), blockchain data also resists random changes that can happen without any intent, such as data corruption on a hard drive. Therefore, in the context of blockchains, we interpret the word “immutable” to mean *practically* immutable, for all intents and purposes. (Linguists would say that the word “immutable” is a _term of art_ in the blockchain community.)

Blockchain data can be made immutable in several ways:

1. **No APIs for changing or deleting data.** Blockchain software usually doesn't expose any APIs for changing or deleting the data stored in the blockchain. BigchainDB has no such APIs. This doesn't prevent changes or deletions from happening in _other_ ways; it's just one line of defense.
1. **Replication.** All data is replicated (copied) to several different places. The higher the replication factor, the more difficult it becomes to change or delete all replicas.
1. **Internal watchdogs.** All nodes monitor all changes and if some unallowed change happens, then appropriate action can be taken.
1. **External watchdogs.** A consortium may opt to have trusted third-parties to monitor and audit their data, looking for irregularities. For a consortium with publicly-readable data, the public can act as an auditor.
1. **Economic incentives.** Some blockchain systems make it very expensive to change old stored data. Examples include proof-of-work and proof-of-stake systems. BigchainDB doesn't use explicit incentives like those.
1. Data can be stored using fancy techniques, such as error-correction codes, to make some kinds of changes easier to undo.
1. **Cryptographic signatures** are often used as a way to check if messages (e.g. transactions) have been tampered with enroute, and as a way to verify who signed the messages. In BigchainDB, each transaction must be signed by one or more parties.
1. **Full or partial backups** may be recorded from time to time, possibly on magnetic tape storage, other blockchains, printouts, etc.
1. **Strong security.** Node owners can adopt and enforce strong security policies.


