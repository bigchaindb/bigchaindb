# Clusters

This section is about how to set up a BigchainDB cluster where each node is operated by a different operator.


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
3. Who will deploy the first node, second node, etc.?

Once those things have been decided, the cluster deployment process can begin. The process for deploying a production node is outlined in [the section on production nodes](../production-nodes/index.html).

Every time a new BigchainDB node is added, every other node must update their [BigchainDB keyring](../server-reference/configuration.html#keyring) (one of the BigchainDB configuration settings): they must add the public key of the new node.

To secure communications between BigchainDB nodes, each BigchainDB node can use a firewall or similar, and doing that will require additional coordination.
