# How BigchainDB is Immutable / Tamper-Resistant

The blockchain community often describes blockchains as “immutable.” If we interpret that word literally, it means that blockchain data is unchangeable or permanent, which is absurd. The data _can_ be changed. For example, a plague might drive humanity extinct; the data would then get corrupted over time due to water damage, thermal noise, and the general increase of entropy. In the case of Bitcoin, nothing so drastic is required: a 51% attack will suffice.

It’s true that blockchain data is more difficult to change than usual: it’s more tamper-resistant than a typical file system or database. Therefore, in the context of blockchains, we interpret the word “immutable” to mean tamper-resistant. (Linguists would say that the word “immutable” is a _term of art_ in the blockchain community.)

BigchainDB achieves strong tamper-resistance in the following ways:

1. **Replication.** All data is sharded and shards are replicated in several (different) places. The replication factor can be set by the federation. The higher the replication factor, the more difficult it becomes to change or delete all replicas.
2. **Unallowed changes get reverted.** If the “bigchain” table is modified via the underlying database’s API, then all nodes are notified of that change. Only two kinds of changes are allowed to persist: 1) addition of a new block or 2) addition of a new vote (not including a “second vote” from a node on a block). All other changes are reverted automatically. For this and other reasons, we suggest that all federations consider the _diversity_ in who controls the servers (federation nodes). We expand on what we mean by diversity below.
3. **Cryptographic signatures** are used throughout BigchainDB as a way to check if messages (transactions, blocks and votes) have been tampered with enroute, and as a way to verify who signed the messages. Each block is signed by the node that created it. Each vote is signed by the node that cast it. A creation transaction is signed by the node that created it, although there are plans to improve that by adding signatures from the sending client and multiple nodes; see [Issue #347](https://github.com/bigchaindb/bigchaindb/issues/347). Transfer transactions can contain multiple fulfillments (one per asset transferred). Each fulfillment will typically contain one or more signatures from the owners (i.e. the owners before the transfer). Hashlock fulfillments are an exception; there’s an open issue ([#339](https://github.com/bigchaindb/bigchaindb/issues/339)) to address that.
4. **Full or partial backups** of the database may be recorded from time to time, possibly on magnetic tape storage, other blockchains, printouts, etc.
5. **Watchdogs.** Federations may opt to have trusted third-parties to  monitor and audit their data, looking for irregularities. For federations with publicly-readable data, the public can act as an auditor.
6. **Strong security.** Node owners can adopt and enforce strong security policies.


## The Kinds of Diversity a Federation Should Consider

Steps should be taken to make it difficult for any one actor or event to control or damage “enough” of the nodes. (“Enough” is usually a quorum.) There are many kinds of diversity to consider, listed below. It may be quite difficult to have high diversity of all kinds.

1. **Jurisdictional diversity.** The nodes should be controlled by entities within multiple legal jurisdictions, so that it becomes difficult to use legal means to compel enough of them to do something.
2. **Geographic diversity.** The servers should be physically located at multiple geographic locations, so that it becomes difficult for a natural disaster (such as a flood or earthquake) to damage enough of them to cause problems.
3. **Hosting diversity.** The servers should be hosted by multiple hosting providers (e.g. Amazon Web Services, Microsoft Azure, Digital Ocean, Rackspace), so that it becomes difficult for one hosting provider to influence enough of the nodes.
4. **Server implementation diversity.** The server software should have multiple independent implementations, so that a single software bug (in one of the implementations) can’t compromise enough the nodes. (This isn’t as practical, but it is worth considering.)
5. **Diversity in general.** In general, membership diversity (of all kinds) confers many advantages on a federation. For example, it provides the federation with a source of various ideas for addressing challenges.
