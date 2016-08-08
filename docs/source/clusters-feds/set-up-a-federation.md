# Set Up a Federation

This section is about how to set up a BigchainDB _federation_, where each node is operated by a different operator. If you want to set up and run a testing cluster on AWS (where all nodes are operated by you), then see [the section about that](aws-testing-cluster.html).


## Initial Checklist

* Do you have a governance process for making federation-level decisions, such as how to admit new members?
* What will you store in creation transactions (data payload)? Is there a data schema?
* Will you use transfer transactions? Will they include a non-empty data payload?
* Who will be allowed to submit transactions? Who will be allowed to read or query transactions? How will you enforce the access rules?


## Set Up the Initial Cluster

The federation must decide some things before setting up the initial cluster (initial set of BigchainDB nodes):

1. Who will operate a node in the initial cluster?
2. What will the replication factor be? (It must be 3 or more for [RethinkDB failover](https://rethinkdb.com/docs/failover/) to work.)
3. Which node will be responsible for sending the commands to configure the RethinkDB database?

Once those things have been decided, each node operator can begin [setting up their BigchainDB (production) node](../prod-node-setup-mgmt/index.html).

Each node operator will eventually need two pieces of information from all other nodes in the federation:

1. Their RethinkDB hostname, e.g. `rdb.farm2.organization.org`
2. Their BigchainDB public key, e.g. `Eky3nkbxDTMgkmiJC8i5hKyVFiAQNmPP4a2G4JdDxJCK`

