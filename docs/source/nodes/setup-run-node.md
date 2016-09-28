# Set Up and Run a Cluster Node

This is a page of general guidelines for setting up a production node. It says nothing about how to upgrade software, storage, processing, etc. or other details of node management. It will be expanded more in the future.


## Get a Server

The first step is to get a server (or equivalent) which meets [the requirements for a BigchainDB node](node-requirements.html).


## Secure Your Server

The steps that you must take to secure your server depend on your server OS and where your server is physically located. There are many articles and books about how to secure a server. Here we just cover special considerations when securing a BigchainDB node.

There are some [notes on BigchainDB-specific firewall setup](../appendices/firewall-notes.html) in the Appendices.


## Sync Your System Clock

A BigchainDB node uses its system clock to generate timestamps for blocks and votes, so that clock should be kept in sync with some standard clock(s). The standard way to do that is to run an NTP daemon (Network Time Protocol daemon) on the node. (You could also use tlsdate, which uses TLS timestamps rather than NTP, but don't: it's not very accurate and it will break with TLS 1.3, which removes the timestamp.)

NTP is a standard protocol. There are many NTP daemons implementing it. We don't recommend a particular one. On the contrary, we recommend that different nodes in a federation run different NTP daemons, so that a problem with one daemon won't affect all nodes.

Please see the [notes on NTP daemon setup](../appendices/ntp-notes.html) in the Appendices.


## Set Up Storage for RethinkDB Data

Below are some things to consider when setting up storage for the RethinkDB data. The Appendices have a [section with concrete examples](../appendices/example-rethinkdb-storage-setups.html).

We suggest you set up a separate storage "device" (partition, RAID array, or logical volume) to store the RethinkDB data. Here are some questions to ask:

* How easy will it be to add storage in the future? Will I have to shut down my server?
* How big can the storage get? (Remember that [RAID](https://en.wikipedia.org/wiki/RAID) can be used to make several physical drives look like one.)
* How fast can it read & write data? How many input/output operations per second (IOPS)?
* How does IOPS scale as more physical hard drives are added?
* What's the latency?
* What's the reliability? Is there replication?
* What's in the Service Level Agreement (SLA), if applicable?
* What's the cost?

There are many options and tradeoffs. Don't forget to look into Amazon Elastic Block Store (EBS) and Amazon Elastic File System (EFS), or their equivalents from other providers.

**Storage Notes Specific to RethinkDB**

* The RethinkDB storage engine has a number of SSD optimizations, so you _can_ benefit from using SSDs. ([source](https://www.rethinkdb.com/docs/architecture/))

* If you want a RethinkDB cluster to store an amount of data D, with a replication factor of R (on every table), and the cluster has N nodes, then each node will need to be able to store R×D/N data.

* RethinkDB tables can have [at most 64 shards](https://rethinkdb.com/limitations/). For example, if you have only one table and more than 64 nodes, some nodes won't have the primary of any shard, i.e. they will have replicas only. In other words, once you pass 64 nodes, adding more nodes won't provide more storage space for new data. If the biggest single-node storage available is d, then the most you can store in a RethinkDB cluster is < 64×d: accomplished by putting one primary shard in each of 64 nodes, with all replica shards on other nodes. (This is assuming one table. If there are T tables, then the most you can store is < 64×d×T.)

* When you set up storage for your RethinkDB data, you may have to select a filesystem. (Sometimes, the filesystem is already decided by the choice of storage.) We recommend using a filesystem that supports direct I/O (Input/Output). Many compressed or encrypted file systems don't support direct I/O. The ext4 filesystem supports direct I/O (but be careful: if you enable the data=journal mode, then direct I/O support will be disabled; the default is data=ordered). If your chosen filesystem supports direct I/O and you're using Linux, then you don't need to do anything to request or enable direct I/O. RethinkDB does that.

<p style="background-color: lightgrey;">What is direct I/O? It allows RethinkDB to write directly to the storage device (or use its own in-memory caching mechanisms), rather than relying on the operating system's file read and write caching mechanisms. (If you're using Linux, a write-to-file normally writes to the in-memory Page Cache first; only later does that Page Cache get flushed to disk. The Page Cache is also used when reading files.)</p>

* RethinkDB stores its data in a specific directory. You can tell RethinkDB _which_ directory using the RethinkDB config file, as explained below. In this documentation, we assume the directory is `/data`. If you set up a separate device (partition, RAID array, or logical volume) to store the RethinkDB data, then mount that device on `/data`.


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
* `direct-io` tells RethinkDB to use direct I/O (explained earlier). Only include this line if your file system supports direct I/O.
* `join=hostname:29015` lines: A cluster node needs to find out the hostnames of all the other nodes somehow. You _could_ designate one node to be the one that every other node asks, and put that node's hostname in the config file, but that wouldn't be very decentralized. Instead, we include _every_ node in the list of nodes-to-ask.

If you're curious about the RethinkDB config file, there's [a RethinkDB documentation page about it](https://www.rethinkdb.com/docs/config-file/). The [explanations of the RethinkDB command-line options](https://rethinkdb.com/docs/cli-options/) are another useful reference.

See the [RethinkDB documentation on securing your cluster](https://rethinkdb.com/docs/security/).


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

BigchainDB (i.e. both the Server and the officially-supported drivers) is distributed as a Python package on PyPI so you can install it using `pip`. First, make sure you have an up-to-date Python 3.4+ version of `pip` installed:
```text
pip -V
```

If it says that `pip` isn't installed, or it says `pip` is associated with a Python version less than 3.4, then you must install a `pip` version associated with Python 3.4+. In the following instructions, we call it `pip3` but you may be able to use `pip` if that refers to the same thing. See [the `pip` installation instructions](https://pip.pypa.io/en/stable/installing/).

On Ubuntu 14.04, we found that this works:
```text
sudo apt-get install python3-pip
```

That should install a Python 3 version of `pip` named `pip3`. If that didn't work, then another way to get `pip3` is to do `sudo apt-get install python3-setuptools` followed by `sudo easy_install3 pip`.

You can upgrade `pip` (`pip3`) and `setuptools` to the latest versions using:
```text
pip3 install --upgrade pip setuptools
pip3 -V
```

Now you can install BigchainDB Server (and officially-supported BigchainDB drivers) using:
```text
pip3 install bigchaindb
```

(If you're not in a virtualenv and you want to install bigchaindb system-wide, then put `sudo` in front.)

Note: You can use `pip3` to upgrade the `bigchaindb` package to the latest version using `pip3 install --upgrade bigchaindb`.


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
