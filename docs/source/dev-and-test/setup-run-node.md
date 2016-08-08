# Set Up & Run a Dev/Test Node

The BigchainDB core dev team develops BigchainDB on Ubuntu 14.04 and Fedora 23, so we recommend you use one of those. BigchainDB Server doesn't work on Windows and Mac OS X (unless you use a VM or containers).

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
