# Set Up a Cluster

This section is about how to set up a BigchainDB cluster where each node is operated by a different operator. If you want to set up and run a testing cluster on AWS (where all nodes are operated by you), then see [the section about that](aws-testing-cluster.html).


## Initial Questions

There are many questions that must be answered before setting up a BigchainDB cluster. For example:

* Do you have a governance process for making consortium-level decisions, such as how to admit new members?
* What will you store in creation transactions (data payload)? Is there a data schema?
* Will you use transfer transactions? Will they include a non-empty data payload?
* Who will be allowed to submit transactions? Who will be allowed to read or query transactions? How will you enforce the access rules?


## Set Up the Initial Cluster

The consortium must decide some things before setting up the initial cluster (initial set of BigchainDB nodes):

1. Who will operate each node in the initial cluster?
2. What will the replication factor be? (It should be 3 or more.)
3. Who will deploy the first node?
4. Who will add subsequent nodes? (It must be one of the existing nodes.)

Once those things have been decided, the cluster deployment process can begin. The process for deploying a production node is outlined in the section on production nodes.

Each BigchainDB node operator will eventually need some information from all other nodes:

1. Their BigchainDB public key, e.g. `Eky3nkbxDTMgkmiJC8i5hKyVFiAQNmPP4a2G4JdDxJCK`
1. Their MongoDB hostname and port, e.g. `mdb.farm2.organization.org:27017`

To secure communications, more information will be needed.
