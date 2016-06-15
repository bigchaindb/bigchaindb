# Set Up and Run a Node

This section goes through the steps to set up a BigchainDB node (running RethinkDB Server, BigchainDB Server, etc.). There are instructions for two cases:

1. Stand-Alone Node (useful for local development)
2. Cluster Node


## Check the Node Requirements

The first step is to make sure you have a server (or equivalent) which meets [the requirements for a BigchainDB node](node-requirements.html).


## System Clock Sync

If you're just setting up a stand-alone node, then you can skip this step.

A BigchainDB node uses its system clock to generate timestamps for blocks and votes, so that clock should be kept in sync with some standard clock(s). The standard way to do that is to run an NTP daemon (Network Time Protocol daemon) on the node. (You could also use tlsdate, which uses TLS timestamps rather than NTP, but don't: it's not very accurate and it will break with TLS 1.3, which removes the timestamp.)

NTP is a standard protocol. There are many NTP daemons implementing it. We don't recommend a particular one. On the contrary, we recommend that different nodes in a federation run different NTP daemons, so that a problem with one daemon won't affect all nodes. Some options are:

* The reference NTP daemon from ntp.org; see [their support website](http://support.ntp.org/bin/view/Support/WebHome)
* [OpenNTPD](http://www.openntpd.org/)
* [chrony](https://chrony.tuxfamily.org/index.html)
* Maybe [NTPsec](https://www.ntpsec.org/), once it's production-ready
* Maybe [Ntimed](http://nwtime.org/projects/ntimed/), once it's production-ready
* [More](https://en.wikipedia.org/wiki/Ntpd#Implementations)

It's tricky to make an NTP daemon setup secure. Always install the latest version and read the documentation about how to configure and run it securely.

The appendix has [some notes on NTP daemon setup](../appendices/ntp-notes.html).


## Set Up the File System for RethinkDB

If you're just setting up a stand-alone node, then you can probably skip this step.

See `def install_rethinkdb()` in `deploy-cluster-aws/fabfile.py` for an example of configuring a file system on an AWS instance running Ubuntu.

TODO: This section needs more elaboration


## Install RethinkDB Server

If you don't already have RethinkDB Server installed, you must install it. The RethinkDB documentation has instructions for [how to install RethinkDB Server on a variety of operating systems](http://rethinkdb.com/docs/install/).


## Configure RethinkDB Server

### Stand-Alone Node

If you're setting up a stand-alone node (i.e. not intending for it to join a cluster), then the default RethinkDB configuration will work.

### Cluster Node

If you're setting up a node that will be part of a RethinkDB cluster, then it needs to find out the hostnames of all the other nodes somehow. You _could_ designate one node to be the one that every other node asks, and put that node's hostname in the RethinkDB config file, but that wouldn't be very decentralized. Instead, we will list _every_ node in the list of nodes-to-ask:

1. Download the [sample RethinkDB config file from RethinkDB](https://github.com/rethinkdb/rethinkdb/blob/next/packaging/assets/config/default.conf.sample).
2. Edit that file to add one line for each node in the federation, like so:
```text
join=node0_hostname:29015
join=node1_hostname:29015
join=node2_hostname:29015
# continue until all federation node hostnames are included
```

where the hostnames must be replaced by the hostnames of the RethinkDB servers in the cluster, e.g. `jackfish.servers.organization45.net`.

You may want to change other things in the RethinkDB config file as well. RethinkDB has [a documentation page with more info](https://www.rethinkdb.com/docs/config-file/).


TODO: Steps to make the RethinkDB cluster more secure.


## Run RethinkDB Server

You can run RethinkDB by opening a Terminal and entering `rethinkdb`. You could do that now or wait until just before you start BigchainDB.


## Install Python 3.4+

If you don't already have it, then you should [install Python 3.4+](https://www.python.org/downloads/) (maybe in a virtual environment, so it doesn't conflict with other Python projects you're working on).


## Install BigchainDB Server

BigchainDB Server has some OS-level dependencies.

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

If you want to install BitchainDB from source because you want to contribute code (i.e. as a BigchainDB developer), then please see the instructions in [the `CONTRIBUTING.md` file](https://github.com/bigchaindb/bigchaindb/blob/master/CONTRIBUTING.md).

Otherwise, clone the public repository:
```text
git clone git@github.com:bigchaindb/bigchaindb.git
```

and then install from source:
```text
python setup.py install
```


## Configure BigchainDB Server

Start by creating a default BigchainDB configuration file (named `.bigchaindb`) in your `$HOME` directory using:
```text
bigchaindb -y configure
```

There's documentation for the `bigchaindb` command is in the section on [the BigchainDB Command Line Interface (CLI)](bigchaindb-cli.html).

### Stand-Alone Node

The default BigchainDB configuration file will work.

### Cluster Node

Open `$HOME/.bigchaindb` in your text editor and:

* Change the keyring (list) to include the public keys of all the other nodes in the federation. The keyring should _not_ include your node's public key.
* TODO: Make other changes to the BigchainDB config file?

For more information about the BigchainDB config file, see [Configuring a BigchainDB Node](configuration.html).


## Run BigchainDB Server

Once you've installed BigchainDB Server, you can run it. First make sure you have RethinkDB running:
```text
rethinkdb
```

You can verify that RethinkDB is running by opening the RethinkDB web interface in your web browser. It should be at `http://rethinkdb-hostname:8080/`. If you're running RethinkDB on localhost, that would be [http://localhost:8080/](http://localhost:8080/).

You can start BigchainDB Server using:
```text
bigchaindb start
```

If it's the first time you've run `bigchaindb start`, then it creates the database (a RethinkDB database), the tables, the indexes, and the genesis block. It then starts BigchainDB. If you're run `bigchaindb start` or `bigchaindb init` before (and you haven't dropped the database), then `bigchaindb start` just starts BigchainDB.


## Run BigchainDB with Docker

**NOT for Production Use**

For those who like using Docker and wish to experiment with BigchainDB in
non-production environments, we currently maintain a Docker image and a
`Dockerfile` that can be used to build an image for `bigchaindb`.

### Pull and Run the Image from Docker Hub

Assuming you have Docker installed, you would proceed as follows.

In a terminal shell, pull the latest version of the BigchainDB Docker image using:
```text
docker pull bigchaindb/bigchaindb
```

then do a one-time configuration step to create the config file; we will use
the `-y` option to accept all the default values. The configuration file will
be stored in a file on your host machine at `~/bigchaindb_docker/.bigchaindb`:

```text
docker run --rm -v "$HOME/bigchaindb_docker:/data" -ti \
  bigchaindb/bigchaindb -y configure
Generating keypair
Configuration written to /data/.bigchaindb
Ready to go!
```

Let's analyze that command:

* `docker run` tells Docker to run some image
* `--rm` remove the container once we are done
* `-v "$HOME/bigchaindb_docker:/data"` map the host directory
 `$HOME/bigchaindb_docker` to the container directory `/data`;
 this allows us to have the data persisted on the host machine,
 you can read more in the [official Docker
 documentation](https://docs.docker.com/engine/userguide/containers/dockervolumes/#mount-a-host-directory-as-a-data-volume)
* `-t` allocate a pseudo-TTY
* `-i` keep STDIN open even if not attached
* `bigchaindb/bigchaindb the image to use
* `-y configure` execute the `configure` sub-command (of the `bigchaindb` command) inside the container, with the `-y` option to automatically use all the default config values


After configuring the system, you can run BigchainDB with the following command:

```text
docker run -v "$HOME/bigchaindb_docker:/data" -d \
  --name bigchaindb \
  -p "58080:8080" -p "59984:9984" \
  bigchaindb/bigchaindb start
```

The command is slightly different from the previous one, the differences are:

* `-d` run the container in the background
* `--name bigchaindb` give a nice name to the container so it's easier to
 refer to it later
* `-p "58080:8080"` map the host port `58080` to the container port `8080`
 (the RethinkDB admin interface)
* `-p "59984:9984"` map the host port `59984` to the container port `9984`
 (the BigchainDB API server)
* `start` start the BigchainDB service

Another way to publish the ports exposed by the container is to use the `-P` (or
`--publish-all`) option. This will publish all exposed ports to random ports. You can
always run `docker ps` to check the random mapping.

You can also access the RethinkDB dashboard at
[http://localhost:58080/](http://localhost:58080/)

If that doesn't work, then replace `localhost` with the IP or hostname of the
machine running the Docker engine. If you are running docker-machine (e.g. on
Mac OS X) this will be the IP of the Docker machine (`docker-machine ip
machine_name`).

#### Load Testing with Docker

Now that we have BigchainDB running in the Docker container named `bigchaindb`, we can
start another BigchainDB container to generate a load test for it.

First, make sure the container named `bigchaindb` is still running. You can check that using:
```text
docker ps
```

You should see a container named `bigchaindb` in the list.

You can load test the BigchainDB running in that container by running the `bigchaindb load` command in a second container:

```text
docker run --rm -v "$HOME/bigchaindb_docker:/data" -ti \
  --link bigchaindb \
  bigchaindb/bigchaindb load
```

Note the `--link` option to link to the first container (named `bigchaindb`).

Aside: The `bigchaindb load` command has several options (e.g. `-m`). You can read more about it in [the documentation about the BigchainDB command line interface](bigchaindb-cli.html).

If you look at the RethinkDB dashboard (in your web browser), you should see the effects of the load test. You can also see some effects in the Docker logs using:
```text
docker logs -f bigchaindb
```

### Building Your Own Image

Assuming you have Docker installed, you would proceed as follows.

In a terminal shell:
```text
git clone git@github.com:bigchaindb/bigchaindb.git
```

Build the Docker image:
```text
docker build --tag local-bigchaindb .
```

Now you can use your own image to run BigchainDB containers.
