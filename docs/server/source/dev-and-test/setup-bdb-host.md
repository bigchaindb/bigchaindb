# Set Up BigchainDB Node on Local Dev Machine

The BigchainDB core dev team develops BigchainDB on recent Ubuntu, Fedora and CentOS distributions, so we recommend you use one of those. BigchainDB Server doesn't work on Windows or macOS (unless you use a VM or containers).


## With MongoDB

First read the BigchainDB [CONTRIBUTING.md file](https://github.com/bigchaindb/bigchaindb/blob/master/CONTRIBUTING.md). It outlines the steps to set up a machine for developing and testing BigchainDB.

Create a default BigchainDB config file (in `$HOME/.bigchaindb`):
```text
$ bigchaindb -y configure mongodb
```

Note: [The BigchainDB CLI](../server-reference/bigchaindb-cli.html) and the [BigchainDB Configuration Settings](../server-reference/configuration.html) are documented elsewhere. (Click the links.)

Start MongoDB __3.4+__ using:
```text
$ mongod --replSet=bigchain-rs
```

You can verify that MongoDB is running correctly by checking the output of the
previous command for the line:
```text
waiting for connections on port 27017
```

To run BigchainDB Server, do:
```text
$ bigchaindb start --init
```

You can [run all the unit tests](running-all-tests.html) to test your installation.


## With RethinkDB

First read the BigchainDB [CONTRIBUTING.md file](https://github.com/bigchaindb/bigchaindb/blob/master/CONTRIBUTING.md). It outlines the steps to set up a machine for developing and testing BigchainDB.

Create a default BigchainDB config file (in `$HOME/.bigchaindb`):
```text
$ bigchaindb -y configure rethinkdb
```

Note: [The BigchainDB CLI](../server-reference/bigchaindb-cli.html) and the [BigchainDB Configuration Settings](../server-reference/configuration.html) are documented elsewhere. (Click the links.)

Start RethinkDB using:
```text
$ rethinkdb
```

You can verify that RethinkDB is running by opening the RethinkDB web interface in your web browser. It should be at http://localhost:8080/

<!-- Don't hyperlink http://localhost:8080/ because Sphinx will fail when you do "make linkcheck" -->

To run BigchainDB Server, do:
```text
$ bigchaindb start --init
```

You can [run all the unit tests](running-all-tests.html) to test your installation.
