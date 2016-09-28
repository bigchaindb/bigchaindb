# Introduction

BigchainDB is a scalable blockchain database. That is, it's a "big data" database with some blockchain characteristics, including [decentralization](topic-guides/decentralized.html), [immutability](topic-guides/immutable.html) and [native support for assets](topic-guides/assets.html).

You can read about the motivations, goals and high-level architecture in the [BigchainDB whitepaper](https://www.bigchaindb.com/whitepaper/).


## Is BigchainDB Production-Ready?

No, BigchainDB is not production-ready. You can use it to build a prototype or proof-of-concept (POC); many people are already doing that.

BigchainDB is currently in version 0.X. ([The Releases page on GitHub](https://github.com/bigchaindb/bigchaindb/releases) has the exact version number.) Once we believe that BigchainDB is production-ready, we'll release version 1.0.

[The BigchainDB Roadmap](https://github.com/bigchaindb/org/blob/master/ROADMAP.md) will give you a sense of the things we intend to do with BigchainDB in the near term and the long term.


## Some Basic Vocabulary

There is some specialized vocabulary associated with BigchainDB. To get started, you should at least know what what we mean by a BigchainDB *node*, *cluster* and *federation*.

A **BigchainDB node** is a machine or set of closely-linked machines running RethinkDB Server, BigchainDB Server, and related software. (A "machine" might be a bare-metal server, a virtual machine or a container.) Each node is controlled by one person or organization.

A set of BigchainDB nodes can connect to each other to form a **cluster**. Each node in the cluster runs the same software. A cluster contains one logical RethinkDB datastore. A cluster may have additional machines to do things such as cluster monitoring.

The people and organizations that run the nodes in a cluster belong to a **federation** (i.e. another organization). A federation must have some sort of governance structure to make decisions. If a cluster is run by a single company, then the federation is just that company.

**What's the Difference Between a Cluster and a Federation?**

A cluster is just a bunch of connected nodes. A federation is an organization which has a cluster, and where each node in the cluster has a different operator. Confusingly, we sometimes call a federation's cluster its "federation." You can probably tell what we mean from context.

There are several kinds of nodes:

- A **dev/test node** is a node created by a developer working on BigchainDB Server, e.g. for testing new or changed code. A dev/test node is typically run on the developer's local machine.

- A **bare-bones node** is a node deployed in the cloud, either as part of a testing cluster or as a starting point before upgrading the node to be production-ready. Our cloud deployment starter templates deploy a bare-bones node, as do our scripts for deploying a testing cluster on AWS.

- A **production node** is a node that is part of a federation's BigchainDB cluster. A production node has the most components and requirements.


## Setup Instructions for Various Cases

* [Set up a local stand-alone BigchainDB node for learning and experimenting: Quickstart](quickstart.html)
* [Set up and run a bare-bones node in the cloud](cloud-deployment-starter-templates/index.html)
* [Set up and run a local dev/test node for developing and testing BigchainDB Server](dev-and-test/setup-run-node.html)
* [Deploy a testing cluster on AWS](clusters-feds/aws-testing-cluster.html)
* [Set up and run a federation (including production nodes)](clusters-feds/set-up-a-federation.html)

Instructions for setting up a client will be provided once there's a public test net.


## Can I Help?

Yes! BigchainDB is an open-source project; we welcome contributions of all kinds. If you want to request a feature, file a bug report, make a pull request, or help in some other way, please see [the CONTRIBUTING.md file](https://github.com/bigchaindb/bigchaindb/blob/master/CONTRIBUTING.md).
