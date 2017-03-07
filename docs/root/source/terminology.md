# Terminology

There is some specialized terminology associated with BigchainDB. To get started, you should at least know what what we mean by a BigchainDB *node*, *cluster* and *consortium*.


## Node

A **BigchainDB node** is a machine or set of closely-linked machines running RethinkDB Server, BigchainDB Server, and related software. (A "machine" might be a bare-metal server, a virtual machine or a container.) Each node is controlled by one person or organization.


## Cluster

A set of BigchainDB nodes can connect to each other to form a **cluster**. Each node in the cluster runs the same software. A cluster contains one logical RethinkDB datastore. A cluster may have additional machines to do things such as cluster monitoring.


## Consortium

The people and organizations that run the nodes in a cluster belong to a **consortium** (i.e. another organization). A consortium must have some sort of governance structure to make decisions. If a cluster is run by a single company, then the "consortium" is just that company.

**What's the Difference Between a Cluster and a Consortium?**

A cluster is just a bunch of connected nodes. A consortium is an organization which has a cluster, and where each node in the cluster has a different operator.