## Workflow to add nodes to a federation
This document describes the process to add a new node to the BigchainDB
 federation.
It is still a work in progress.


### Prerequisite:
1.  You should have a single node BigchainDB cluster with a MongoDB backend
 running. Or a minimum of a single mongodb node running. We will call it the
 'existing cluster.'

2.  The initial cluster should be able to access the new cluster over the
 network. More specifically, the mongo-host:27017 should be accessible for
 mongodb's intra-cluster communication, and the bdb-host:9984 should be
 accessible globally for the HTTP API to work.

### Ideal Steps:
1.  Spin up a new mongo node with the host name of the existing replica set.
 This can be done by leveraging ConfigMaps in Kubernetes.
2.  Add the public key of the existing BigchainDB node to the new node's
 keyring.
3.  Shut down the existing BigchainDB node and add the public key of the new
 node to it's keyring.

### Plan of action/Task breakdown
 - [ ] Spin up a one node mongodb cluster on Kubernetes, and allow TCP:27017
 access globally.
 - [ ] Spin up another Kubernetes cluster (without starting the MongoDB
 StatefulSet), append the hostname of existing mongodb to the ConfigMap.
 - [ ] Populate the env var inside mongo container to allow it to connect to
 the existing instance OR change the mongo config file. This can be achieved
 by deriving a new container from mongo:3.4.1 container OR leverage Kubernetes
 config some way. This should become clear as we move ahead. We will have a
 mongodb cluster up and running at this point.
 - [ ] BigchainDB cluster to be updated manually. Exact steps will be
 documented as we move ahead.
