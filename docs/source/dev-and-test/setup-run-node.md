# Set Up & Run a Dev/Test Node

This page explains how to set up a minimal local BigchainDB node for development and testing purposes.

The BigchainDB core dev team develops BigchainDB on recent Ubuntu and Fedora distributions, so we recommend you use one of those. BigchainDB Server doesn't work on Windows and Mac OS X (unless you use a VM or containers).


## Option A: Using a Local Dev Machine

First, read through the BigchainDB [CONTRIBUTING.md file](https://github.com/bigchaindb/bigchaindb/blob/master/CONTRIBUTING.md). It outlines the steps to setup a machine for developing and testing BigchainDB.

Next, create a default BigchainDB config file (in `$HOME/.bigchaindb`):
```text
bigchaindb -y configure
```

Note: [The BigchainDB CLI](../server-reference/bigchaindb-cli.html) and the [BigchainDB Configuration Settings](../server-reference/configuration.html) are documented elsewhere. (Click the links.)

Start RethinkDB using:
```text
rethinkdb
```

You can verify that RethinkDB is running by opening the RethinkDB web interface in your web browser. It should be at [http://localhost:8080/](http://localhost:8080/).

To run BigchainDB Server, do:
```text
bigchaindb start
```

You can [run all the unit tests](running-unit-tests.html) to test your installation.

The BigchainDB [CONTRIBUTING.md file](https://github.com/bigchaindb/bigchaindb/blob/master/CONTRIBUTING.md) has more details about how to contribute.


## Option B: Using a Dev Machine on Cloud9

Ian Worrall of [Encrypted Labs](http://www.encryptedlabs.com/) wrote a document (PDF) explaining how to set up a BigchainDB (Server) dev machine on [Cloud9](https://c9.io/):

[Launching BigchainDB on Cloud9 Dev Environment.pdf](https://github.com/bigchaindb/bigchaindb/raw/master/docs/source/_static/cloud9.pdf)
