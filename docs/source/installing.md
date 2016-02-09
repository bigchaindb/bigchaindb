# Installing BigchainDB

BigchainDB works on top of [rethinkDB](http://rethinkdb.com/) server. In order to use
BigchainDB we first need to install rethinkDB server.

##### Installing and running rethinkDB server on Ubuntu >= 12.04

Rethinkdb provides binaries for all major distros. For ubuntu we only need to
add the [RethinkDB repository](http://download.rethinkdb.com/apt/) to our list
of repositories and install via `apt-get`

```shell
source /etc/lsb-release && echo "deb http://download.rethinkdb.com/apt
$DISTRIB_CODENAME main" | sudo tee /etc/apt/sources.list.d/rethinkdb.list
wget -qO- https://download.rethinkdb.com/apt/pubkey.gpg | sudo apt-key add -
sudo apt-get update
sudo apt-get install rethinkdb
```

For more information, rethinkDB provides [detailed
instructions](http://rethinkdb.com/docs/install/) on how to install in a variety
of systems.

RethinkDB does not require any special configuration. To start rethinkdb server
just run this command on the terminal.

```shell
$ rethinkdb
```

##### Installing and running BigchainDB
BigchainDB is distributed as a python package. Installing is simple using `pip`

```shell
$ pip install bigchaindb
```

After installing BigchainDB we can run it with:

```shell
$ bigchaindb start
```

During the first run BigchainDB takes care of configuring a single node
environment.

##### Installing from source

BigchainDB is in its early stages and being actively developed on its [GitHub
repository](https://github.com/BigchainDB/bigchaindb). Contributions are highly
appreciated.

Clone the public repository
```shell
$ git clone git@github.com:BigchainDB/bigchaindb.git
```

Install from the source
```shell
$ python setup.py install
```

##### Installing with Docker?
Coming soon...
