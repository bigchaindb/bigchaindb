<!---
Copyright © 2020 Interplanetary Database Association e.V.,
BigchainDB and IPDB software contributors.
SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
Code is Apache-2.0 and docs are CC-BY-4.0
--->

# Production Node Assumptions

Be sure you know the key BigchainDB terminology:

* [BigchainDB node, BigchainDB network and BigchainDB consortium](https://docs.bigchaindb.com/en/latest/terminology.html)

Note that there are a few kinds of nodes:

- A **dev/test node** is a node created by a developer working on BigchainDB Server, e.g. for testing new or changed code. A dev/test node is typically run on the developer's local machine.

- A **bare-bones node** is a node deployed in the cloud, either as part of a testing network or as a starting point before upgrading the node to be production-ready.

- A **production node** is a node that is part of a consortium's BigchainDB network. A production node has the most components and requirements.

We make some assumptions about production nodes:

1. Each production node is set up and managed by an experienced professional system administrator or a team of them.
1. Each production node in a network is managed by a different person or team.
