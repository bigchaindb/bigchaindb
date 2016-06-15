# Set Up and Run a Federation

This section is about how to set up and run a BigchainDB _federation_, where each node is operated by a different operator. If you want to set up and run a BigchainDB cluster on AWS (where all nodes are operated by you), then see [the section about that](deploy-on-aws.html).


## Initial Checklist

* Do you have a governance process for making federation-level decisions, such as how to admit new members?
* What will you store in creation transactions (data payload)? Is there a data schema?
* Will you use transfer transactions? Will they include a non-empty data payload?
* Who will be allowed to submit transactions? Who will be allowed to read or query transactions? How will you enforce the access rules?


## Set Up the Initial Cluster

When you first start a federation cluster, the initial nodes will all start at roughly the same time.

The steps to set up a cluster node are outlined in the section titled [Set Up and Run a Node](../nodes/setup-run-node.html). You'll need two pieces of information from all other nodes in the federation:

1. Their RethinkDB hostname, e.g. `rdb.farm2.organization.org`
2. Their BigchainDB public key, e.g. `Eky3nkbxDTMgkmiJC8i5hKyVFiAQNmPP4a2G4JdDxJCK`


## Documentation to Come

* Backing Up & Restoring data
* Adding a node (including resharding etc.)
* Removing a node
* Logging
* Node monitoring & crash recovery
* Node Security
    * Securing your OS
    * Firewalls and security groups. Remember to open port 123 for NTP.
    * (Private) key management
    * RethinkDB security
* Cluster monitoring
* Internal watchdogs
* External watchdogs