# Introduction

This is the documentation for BigchainDB Server, the BigchainDB software that one runs on servers (but not on clients).

If you want to use BigchainDB Server, then you should first understand what BigchainDB is, plus some of the specialized BigchaindB terminology. You can read about that in [the overall BigchainDB project documentation](https://docs.bigchaindb.com/en/latest/index.html).

Note that there are a few kinds of nodes:

- A **dev/test node** is a node created by a developer working on BigchainDB Server, e.g. for testing new or changed code. A dev/test node is typically run on the developer's local machine.

- A **bare-bones node** is a node deployed in the cloud, either as part of a testing cluster or as a starting point before upgrading the node to be production-ready.

- A **production node** is a node that is part of a consortium's BigchainDB cluster. A production node has the most components and requirements.


## Setup Instructions for Various Cases

* [Set up a local stand-alone BigchainDB node for learning and experimenting: Quickstart](quickstart.html)
* [Set up and run a local dev/test node for developing and testing BigchainDB Server](dev-and-test/setup-run-node.html)
* [Set up and run a cluster (including production nodes)](clusters-feds/set-up-a-cluster.html)

There are some old RethinkDB-based deployment instructions as well:

* [Deploy a bare-bones RethinkDB-based node on Azure](appendices/azure-quickstart-template.html)
* [Deploy a bare-bones RethinkDB-based node on any Ubuntu machine with Ansible](appendices/template-ansible.html)
* [Deploy a RethinkDB-based testing cluster on AWS](appendices/aws-testing-cluster.html)

Instructions for setting up a client will be provided once there's a public test net.


## Can I Help?

Yes! BigchainDB is an open-source project; we welcome contributions of all kinds. If you want to request a feature, file a bug report, make a pull request, or help in some other way, please see [the CONTRIBUTING.md file](https://github.com/bigchaindb/bigchaindb/blob/master/CONTRIBUTING.md).
