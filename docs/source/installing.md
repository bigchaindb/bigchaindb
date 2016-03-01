# Installing BigchainDB Server

We're developing BigchainDB Server ("BigchainDB") on Ubuntu 14.04, but it should work on any OS that runs RethinkDB Server and Python 3.4+. (BigchainDB is built on top of RethinkDB Server.)

BigchainDB Server is intended to be run on each server in a large distributed cluster of servers; it's not very useful running by itself on a single computer. That's _why_ we're developing it on Ubuntu 14.04: it's one of the more common server operating systems.

Mac OS X users may get the best results [running BigchainDB Server with Docker](https://bigchaindb.readthedocs.org/en/develop/installing.html#run-bigchaindb-with-docker).

Windows users may get the best results [running BigchainDB Server in a VM with Vagrant](https://bigchaindb.readthedocs.org/en/develop/installing.html#how-to-install-bigchaindb-on-a-vm-with-vagrant).

(Right now, there are no BigchainDB clients/drivers. Those will be able to run on a much larger array of operating systems. They're coming soon.)

## Install and Run RethinkDB Server

The RethinkDB documentation has instructions for how to install RethinkDB Server on a variety of operating systems. Do that (using their instructions for your OS): [Install RethinkDB Server](http://rethinkdb.com/docs/install/).

RethinkDB Server doesn't require any special configuration. You can run it by opening a Terminal and entering:
```text
$ rethinkdb
```

## Install Python 3.4+

If you don't already have it, then you should [install Python 3.4+](https://www.python.org/downloads/) (maybe in a virtual environment, so it doesn't conflict with other Python projects you're working on).

## Install BigchainDB

BigchainDB has some OS-level dependencies. In particular, you need to install the OS-level dependencies for the Python **cryptography** package. Instructions for installing those dependencies on your OS can be found in the [cryptography package documentation](https://cryptography.io/en/latest/installation/).

On Ubuntu 14.04, we found that the following was enough:
```text
$ sudo apt-get update
$ sudo apt-get install libffi-dev g++ libssl-dev python3-dev
```

On Fedora 23, we found that the following was enough (tested in February 2015):
```text
$ sudo dnf update
$ sudo dnf install libffi-devel gcc-c++ redhat-rpm-config python3-devel openssl-devel
```

(If you're using a version of Fedora before version 22, you may have to use `yum` instead of `dnf`.)

With OS-level dependencies installed, you can install BigchainDB with `pip` or from source.

### How to Install BigchainDB with `pip`

BigchainDB is distributed as a Python package on PyPI so you can install it using `pip`. First, make sure you have a version of `pip` installed for Python 3.4+:
```text
$ pip -V
```

If it says that `pip` isn't installed, or it says `pip` is associated with a Python version less than 3.4, then you must install a `pip` version associated with Python 3.4+. See [the `pip` installation instructions](https://pip.pypa.io/en/stable/installing/). On Ubuntu 14.04, we found that this works:
```text
$ sudo apt-get install python3-setuptools
$ sudo easy_install3 pip
```
(Note: Using `sudo apt-get python3-pip` also installs a Python 3 version of `pip` (named `pip3`) but we found it installed a very old version and there were issues with updating it.)

Once you have a version of `pip` associated with Python 3.4+, then you can install BigchainDB using:
```text
sudo pip install bigchaindb
```
(or maybe `sudo pip3 install bigchaindb` or `sudo pip3.4 install bigchaindb`. The `sudo` may not be necessary.)

Note: You can use `pip` to upgrade bigchaindb to the latest version using `sudo pip install --upgrade bigchaindb`

### How to Install BigchainDB from Source

BigchainDB is in its early stages and being actively developed on its [GitHub repository](https://github.com/bigchaindb/bigchaindb). Contributions are highly appreciated.

Clone the public repository:
```text
$ git clone git@github.com:bigchaindb/bigchaindb.git
```

Install from the source:
```text
$ python setup.py install
```

### How to Install BigchainDB on a VM with Vagrant

One of our community members ([@Mec-Is](https://github.com/Mec-iS)) wrote [a page about how to install BigchainDB on a VM with Vagrant](https://gist.github.com/Mec-iS/b84758397f1b21f21700).


## Run BigchainDB

Once you've installed BigchainDB, you can run it. First make sure you have RethinkDB running:
```text
$ rethinkdb
```

Then open a different terminal and run:
```text
$ bigchaindb start
```

During its first run, BigchainDB takes care of configuring a single node environment.


## Run BigchainDB with Docker

**NOT for Production Use**

For those who like using Docker and wish to experiment with BigchainDB in
non-production environments, we currently maintain a `dockerfile` that can be
used to build an image for `bigchaindb`, along with a `docker-compose.yml` file
to manage a "standalone node", consisting mainly of two containers: one for
RethinkDB, and another for BigchainDB.

Assuming you have `docker` and `docker-compose` installed, you would proceed as
follows.

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
```

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

If that doesn't work, then replace `localhost` 
with the IP or hostname of the machine running the Docker engine. 
If you are running docker-machine (e.g.: on Mac OS X) this will be the
IP of the Docker machine (`docker-machine ip machine_name`).
