# Set Up and Run a Cluster Node

If you want to set up a BigchainDB node that's intended to be one of the nodes in a BigchainDB cluster (i.e. where each node is operated by a different member of a federation), then this page is for you, otherwise see [elsewhere](../introduction.html).


## Get a Server

The first step is to get a server (or equivalent) which meets [the requirements for a BigchainDB node](node-requirements.html).


## Secure Your Server

The steps that you must take to secure your server depend on your server OS and where your server is physically located. There are many articles and books about how to secure a server. Ask a search engine.

Here we just cover special considerations when securing a BigchainDB node.

TODO: Special security considerations for BigchainDB nodes.

TODO: Notes about firewall setup. What ports should be open, for what kinds of traffic, accepting connections from what IP addresses, etc. For example, NTP uses port 123. Can firewall setup be done now or does it have to happen later?


## Sync Your System Clock

A BigchainDB node uses its system clock to generate timestamps for blocks and votes, so that clock should be kept in sync with some standard clock(s). The standard way to do that is to run an NTP daemon (Network Time Protocol daemon) on the node. (You could also use tlsdate, which uses TLS timestamps rather than NTP, but don't: it's not very accurate and it will break with TLS 1.3, which removes the timestamp.)

NTP is a standard protocol. There are many NTP daemons implementing it. We don't recommend a particular one. On the contrary, we recommend that different nodes in a federation run different NTP daemons, so that a problem with one daemon won't affect all nodes.

Please see the [notes on NTP daemon setup in the Appendices](../appendices/ntp-notes.html).


## Set Up the File System for RethinkDB

Ideally, use a file system that supports direct I/O (Input/Output), a feature whereby file reads and writes go directly from RethinkDB to the storage device, bypassing the operating system read and write caches.

TODO: What file systems support direct I/O? How can you check? How do you enable it, if necessary?

See `def install_rethinkdb()` in `deploy-cluster-aws/fabfile.py` for an example of configuring a file system on an AWS instance running Ubuntu.

Mount the partition for RethinkDB on `/data`: we will tell RethinkDB to store its data there.

TODO: This section needs more elaboration


## Install RethinkDB Server

If you don't already have RethinkDB Server installed, you must install it. The RethinkDB documentation has instructions for [how to install RethinkDB Server on a variety of operating systems](http://rethinkdb.com/docs/install/).


## Configure RethinkDB Server

Create a RethinkDB configuration file (text file) named `instance1.conf` with the following contents (explained below):
```text
directory=/data
bind=all
direct-io
# Replace node?_hostname with actual node hostnames below, e.g. rdb.examples.com
join=node0_hostname:29015
join=node1_hostname:29015
join=node2_hostname:29015
# continue until there's a join= line for each node in the federation
```

* `directory=/data` tells the RethinkDB node to store its share of the database data in `/data`.
* `bind=all` binds RethinkDB to all local network interfaces (e.g. loopback, Ethernet, wireless, whatever is available), so it can communicate with the outside world. (The default is to bind only to local interfaces.)
* `direct-io` tells RethinkDB to use direct I/O (explained earlier).
* `join=hostname:29015` lines: A cluster node needs to find out the hostnames of all the other nodes somehow. You _could_ designate one node to be the one that every other node asks, and put that node's hostname in the config file, but that wouldn't be very decentralized. Instead, we include _every_ node in the list of nodes-to-ask.

If you're curious about the RethinkDB config file, there's [a RethinkDB documentation page about it](https://www.rethinkdb.com/docs/config-file/). The [explanations of the RethinkDB command-line options](https://rethinkdb.com/docs/cli-options/) are another useful reference.

TODO: Explain how to configure the RethinkDB cluster to be more secure.


## Install Python 3.4+

If you don't already have it, then you should [install Python 3.4+](https://www.python.org/downloads/).

If you're testing or developing BigchainDB on a stand-alone node, then you should probably create a Python 3.4+ virtual environment and activate it (e.g. using virtualenv or conda). Later we will install several Python packages and you probably only want those installed in the virtual environment.


## Install BigchainDB Server

BigchainDB Server has some OS-level dependencies that must be installed.

On Ubuntu 14.04, we found that the following was enough:
```text
sudo apt-get update
sudo apt-get install g++ python3-dev
```

On Fedora 23, we found that the following was enough (tested in February 2015):
```text
sudo dnf update
sudo dnf install gcc-c++ redhat-rpm-config python3-devel
```

(If you're using a version of Fedora before version 22, you may have to use `yum` instead of `dnf`.)

With OS-level dependencies installed, you can install BigchainDB Server with `pip` or from source.


### How to Install BigchainDB with pip

BigchainDB (i.e. both the Server and the officially-supported drivers) is distributed as a Python package on PyPI so you can install it using `pip`. First, make sure you have a version of `pip` installed for Python 3.4+:
```text
pip -V
```

If it says that `pip` isn't installed, or it says `pip` is associated with a Python version less than 3.4, then you must install a `pip` version associated with Python 3.4+. See [the `pip` installation instructions](https://pip.pypa.io/en/stable/installing/). On Ubuntu 14.04, we found that this works:
```text
sudo apt-get install python3-setuptools
sudo easy_install3 pip
pip3 install --upgrade pip wheel setuptools
```

(Note: Using `sudo apt-get python3-pip` also installs a Python 3 version of `pip` (named `pip3`) but we found it installed a very old version and there were issues with updating it.)

Once you have a version of `pip` associated with Python 3.4+, then you can install BigchainDB Server (and officially-supported BigchainDB drivers) using:
```text
sudo pip install bigchaindb
```
(or maybe `sudo pip3 install bigchaindb` or `sudo pip3.4 install bigchaindb`. The `sudo` may not be necessary.)

Note: You can use `pip` to upgrade the `bigchaindb` package to the latest version using `sudo pip install --upgrade bigchaindb`

### How to Install BigchainDB from Source

If you want to install BitchainDB from source because you want to use the very latest bleeding-edge code, clone the public repository:
```text
git clone git@github.com:bigchaindb/bigchaindb.git
python setup.py install
```


## Configure BigchainDB Server

Start by creating a default BigchainDB config file:
```text
bigchaindb -y configure
```

(There's documentation for the `bigchaindb` command is in the section on [the BigchainDB Command Line Interface (CLI)](bigchaindb-cli.html).)

Edit the created config file: 

* Open `$HOME/.bigchaindb` (the created config file) in your text editor.
* Change `"server": {"bind": "localhost:9984", ... }` to `"server": {"bind": "0.0.0.0:9984", ... }`. This makes it so traffic can come from any IP address to port 9984 (the HTTP Client-Server API port).
* Change `"api_endpoint": "http://localhost:9984/api/v1"` to `"api_endpoint": "http://your_api_hostname:9984/api/v1"`
* Change `"keyring": []` to `"keyring": ["public_key_of_other_node_A", "public_key_of_other_node_B", "..."]` i.e. a list of the public keys of all the other nodes in the federation. The keyring should _not_ include your node's public key.

For more information about the BigchainDB config file, see [Configuring a BigchainDB Node](configuration.html).


## Run RethinkDB Server

Start RethinkDB using:
```text
rethinkdb --config-file path/to/instance1.conf
```

except replace the path with the actual path to `instance1.conf`.

Note: It's possible to [make RethinkDB start at system startup](https://www.rethinkdb.com/docs/start-on-startup/).

You can verify that RethinkDB is running by opening the RethinkDB web interface in your web browser. It should be at `http://rethinkdb-hostname:8080/`. If you're running RethinkDB on localhost, that would be [http://localhost:8080/](http://localhost:8080/).


## Run BigchainDB Server

After all node operators have started RethinkDB, but before they start BigchainDB, one designated node operator must configure the RethinkDB database by running the following commands:
```text
bigchaindb init
bigchaindb set-shards numshards
bigchaindb set-replicas numreplicas
```

where:

* `bigchaindb init` creates the database within RethinkDB, the tables, the indexes, and the genesis block.
* `numshards` should be set to the number of nodes in the initial cluster.
* `numreplicas` should be set to the database replication factor decided by the federation. It must be 3 or more for [RethinkDB failover](https://rethinkdb.com/docs/failover/) to work.

Once the RethinkDB database is configured, every node operator can start BigchainDB using:
```text
bigchaindb start
```
