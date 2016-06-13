# Set Up and Run a Node

First make sure your server(s) meet [the requirements for a BigchainDB node](node-requirements.html).

Mac OS X users may get the best results [running BigchainDB Server with Docker](setup-run-node.html#run-bigchaindb-with-docker).

We currently don't test BigchainDB on Windows. If you run into problems on Windows, then you may want to try [using Vagrant](setup-run-node.html#how-to-install-bigchaindb-on-a-vm-with-vagrant).


## Install and Run RethinkDB Server

If you don't already have RethinkDB Server installed, you must install it. The RethinkDB documentation has instructions for [how to install RethinkDB Server on a variety of operating systems](http://rethinkdb.com/docs/install/).

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
$ pip3 install --upgrade pip wheel setuptools
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
$ docker run --rm -v "$HOME/bigchaindb_docker:/data" -ti \
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
$ docker run -v "$HOME/bigchaindb_docker:/data" -d \
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
$ docker run --rm -v "$HOME/bigchaindb_docker:/data" -ti \
  --link bigchaindb \
  bigchaindb/bigchaindb load
```

Note the `--link` option to link to the first container (named `bigchaindb`).

Aside: The `bigchaindb load` command has several options (e.g. `-m`). You can read more about it in [the documentation about the BigchainDB command line interface](bigchaindb-cli.html).

If you look at the RethinkDB dashboard (in your web browser), you should see the effects of the load test. You can also see some effects in the Docker logs using:
```text
$ docker logs -f bigchaindb
```

### Building Your Own Image

Assuming you have Docker installed, you would proceed as follows.

In a terminal shell:
```text
$ git clone git@github.com:bigchaindb/bigchaindb.git
```

Build the Docker image:
```text
$ docker build --tag local-bigchaindb .
```

Now you can use your own image to run BigchainDB containers.
