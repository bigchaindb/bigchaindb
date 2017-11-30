# Terminology

There is some specialized terminology associated with BigchainDB. To get started, you should at least know the following:

## BigchainDB Node

A **BigchainDB node** is a machine (or logical machine) running [BigchainDB Server](https://docs.bigchaindb.com/projects/server/en/latest/introduction.html) and related software. Each node is controlled by one person or organization.

## BigchainDB Cluster

A set of BigchainDB nodes can connect to each other to form a **BigchainDB cluster**. Each node in the cluster runs the same software. A cluster may have additional machines to do things such as cluster monitoring.

## BigchainDB Consortium

The people and organizations that run the nodes in a cluster belong to a **BigchainDB consortium** (i.e. another organization). A consortium must have some sort of governance structure to make decisions. If a cluster is run by a single company, then the "consortium" is just that company.

**What's the Difference Between a Cluster and a Consortium?**

A cluster is just a bunch of connected nodes. A consortium is an organization which has a cluster, and where each node in the cluster has a different operator.