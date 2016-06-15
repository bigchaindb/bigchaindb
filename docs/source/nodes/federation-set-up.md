# Set Up and Run a Federation

This section is about how to set up and run a BigchainDB _federation_, where each node is operated by a different operator. If you want to set up and run a BigchainDB cluster on AWS (where all nodes are operated by you), then see [the section about that](deploy-on-aws.html).


## Answer Basic Questions

* Do you have a governance process for making federation-level decisions, such as how to admit new members?
* What will you store in creation transactions (data payload)? Is there a data schema?
* Will you use transfer transactions? Will they include a non-empty data payload?
* Who will be allowed to submit transactions? Who will be allowed to read or query transactions? How will you enforce the access rules?


## Set Up the Initial Cluster

When you first start a federation cluster, the initial nodes will all start at roughly the same time. Here are the steps to be taken by each node operator:

**Create a RethinkDB Cluster**

* Go through the steps of [Set Up and Run a Node](setup-run-node.html), up to "Configure RethinkDB Server"
* Determine the hostname of the server running RethinkDB (e.g. `rethinkdb2.farm3.organization5.com`)
* Share your RethinkDB hostname with all other members of the federation
* Once you have all the RethinkDB hostnames, add them to your local RethinkDB configuration file as explained in [Configure RethinkDB Server](setup-run-node.html#configure-rethinkdb-server)
* (TODO: Section with steps to make RethinkDB more secure)

**Install, Configure and Run BigchainDB**

* Continue with the steps of [Set Up and Run a Node](setup-run-node.html)
* You will generate a default `.bigchaindb` config file at some point. It contains your public/private keypair.
* Send your **public** key to all other federation members. If you accidentally send your private key, then delete your `.bigchaindb` config file, generate a new one, and send your new public key to all other federation members.
* Once you have the public keys of all other federation members, put them in the `keyring` (list) in your `.bigchaindb` file. (Your keyring should _not_ include your public key.)

* TODO: Are there other things they should change in their `.bigchaindb` file?

* Make sure RethinkDB is Running (TODO: say how)
* Start BigchainDB

```text
$ bigchaindb start
```



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