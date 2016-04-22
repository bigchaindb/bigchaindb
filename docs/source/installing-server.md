# Installing and Running BigchainDB Server

We're developing BigchainDB Server on Ubuntu 14.04, but it should work on any OS that runs RethinkDB Server and Python 3.4+. (BigchainDB Server is built on top of RethinkDB Server.)

BigchainDB Server is intended to be run on each server in a large distributed cluster of servers; it's not very useful running by itself on a single computer. That's _why_ we're developing it on Ubuntu 14.04: it's one of the more common server operating systems.

Mac OS X users may get the best results [running BigchainDB Server with Docker](installing-server.html#run-bigchaindb-with-docker).

Windows users may get the best results [running BigchainDB Server in a VM with Vagrant](installing-server.html#how-to-install-bigchaindb-on-a-vm-with-vagrant).

(BigchainDB clients should run on a much larger array of operating systems.)


## Install and Run RethinkDB Server

If you don't already have RethinkDB Server installed on your server, you must install it. The RethinkDB documentation has instructions for [how to install RethinkDB Server on a variety of operating systems](http://rethinkdb.com/docs/install/).

RethinkDB Server doesn't require any special configuration. You can run it by opening a Terminal and entering:
```text
$ rethinkdb
```

## Install Python 3.4+

If you don't already have it, then you should [install Python 3.4+](https://www.python.org/downloads/) (maybe in a virtual environment, so it doesn't conflict with other Python projects you're working on).

## Install BigchainDB Server

BigchainDB Server has some OS-level dependencies.

On Ubuntu 14.04, we found that the following was enough:
```text
$ sudo apt-get update
$ sudo apt-get install g++ python3-dev
```

On Fedora 23, we found that the following was enough (tested in February 2015):
```text
$ sudo dnf update
$ sudo dnf install gcc-c++ redhat-rpm-config python3-devel
```

(If you're using a version of Fedora before version 22, you may have to use `yum` instead of `dnf`.)

With OS-level dependencies installed, you can install BigchainDB Server with `pip` or from source.

### How to Install BigchainDB with pip

BigchainDB (i.e. both the Server and the officially-supported drivers) is distributed as a Python package on PyPI so you can install it using `pip`. First, make sure you have a version of `pip` installed for Python 3.4+:
```text
$ pip -V
```

If it says that `pip` isn't installed, or it says `pip` is associated with a Python version less than 3.4, then you must install a `pip` version associated with Python 3.4+. See [the `pip` installation instructions](https://pip.pypa.io/en/stable/installing/). On Ubuntu 14.04, we found that this works:
```text
$ sudo apt-get install python3-setuptools
$ sudo easy_install3 pip
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
$ git clone git@github.com:bigchaindb/bigchaindb.git
```

and then install from source:
```text
$ python setup.py install
```

### How to Install BigchainDB on a VM with Vagrant

One of our community members ([@Mec-Is](https://github.com/Mec-iS)) wrote [a page about how to install BigchainDB on a VM with Vagrant](https://gist.github.com/Mec-iS/b84758397f1b21f21700).


## Run BigchainDB Server

Once you've installed BigchainDB Server, you can run it. First make sure you have RethinkDB running:
```text
$ rethinkdb
```

Then open a different terminal and run:
```text
$ bigchaindb -y configure
```

That creates a configuration file in `$HOME/.bigchaindb` (documented in [the section on configuration](configuration.html)). More documentation about the `bigchaindb` command is in the section on [the BigchainDB Command Line Interface (CLI)](bigchaindb-cli.html).

You can start BigchainDB Server using:
```text
$ bigchaindb start
```

If it's the first time you've run `bigchaindb start`, then it creates the database (a RethinkDB database), the tables, the indexes, and the genesis block. It then starts BigchainDB. If you're run `bigchaindb start` or `bigchaindb init` before (and you haven't dropped the database), then `bigchaindb start` just starts BigchainDB.


## Run BigchainDB with Docker

**NOT for Production Use**

For those who like using Docker and wish to experiment with BigchainDB in non-production environments, we currently maintain a `dockerfile` that can be used to build an image for `bigchaindb`, along with a `docker-compose.yml` file to manage a "standalone node", consisting mainly of two containers: one for RethinkDB, and another for BigchainDB.

Assuming you have `docker` and `docker-compose` installed, you would proceed as follows.

In a terminal shell:
```text
$ git clone git@github.com:bigchaindb/bigchaindb.git
```

Build the Docker image:
```text
$ docker-compose build
```

then do a one-time configuration step to create the config file; it will be
stored on your host machine under ` ~/.bigchaindb_docker/config`:
```text
$ docker-compose run --rm bigchaindb bigchaindb configure
Starting bigchaindb_rethinkdb-data_1
Generating keypair
API Server bind? (default `localhost:9984`): 
Database host? (default `localhost`): rethinkdb
Database port? (default `28015`): 
Database name? (default `bigchain`): 
Statsd host? (default `localhost`): statsd
Statsd port? (default `8125`): 
Statsd rate? (default `0.01`): 
Ready to go!
```

As shown above, make sure that you set the database and statsd hosts to their
corresponding service names (`rethinkdb`, `statsd`), defined in`docker-compose.yml`
and `docker-compose-monitor.yml`.

You can then start it up (in the background, as a daemon) using:
```text
$ docker-compose up -d
```

then you can load test transactions via:
```text
$ docker-compose run --rm bigchaindb bigchaindb-benchmark load
```

If you're on Linux, you can probably view the RethinkDB dashboard at:

[http://localhost:58080/](http://localhost:58080/)

If that doesn't work, then replace `localhost` with the IP or hostname of the machine running the Docker engine. If you are running docker-machine (e.g.: on Mac OS X) this will be the IP of the Docker machine (`docker-machine ip machine_name`).
