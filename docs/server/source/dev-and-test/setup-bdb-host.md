#### Set up BigchainDB node on Local Dev Machine

### With RethinkDB

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
$ bigchaindb start
```

You can [run all the unit tests](running-unit-tests.html) to test your installation.

The BigchainDB [CONTRIBUTING.md file](https://github.com/bigchaindb/bigchaindb/blob/master/CONTRIBUTING.md) has more details about how to contribute.


### With MongoDB

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
$ bigchaindb start
```

You can [run all the unit tests](running-unit-tests.html) to test your installation.

The BigchainDB [CONTRIBUTING.md file](https://github.com/bigchaindb/bigchaindb/blob/master/CONTRIBUTING.md) has more details about how to contribute.