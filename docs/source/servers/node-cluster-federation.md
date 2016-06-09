# Terminology: Nodes, Clusters & Federations

A **BigchainDB node** is a server or set of closely-linked servers running RethinkDB Server, BigchainDB Server, and other BigchainDB-related software. Each node is controlled by one person or organization.

A set of BigchainDB nodes can connect to each other to form a **cluster**. Each node in the cluster runs the same software. A cluster contains one logical RethinkDB datastore. A cluster may have additional servers to do things such as cluster monitoring.

The people and organizations that run the nodes in a cluster belong to a **federation** (i.e. another organization, although it may be quite informal). A federation might be an organization in its own right, with a governance structure and executives. Confusingly, sometimes we refer to a cluster as a federation. You can probably tell what we mean from context.