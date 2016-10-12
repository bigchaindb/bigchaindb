# Set Up & Run a Dev/Test Node

This page explains how to set up a minimal local BigchainDB node for development and testing purposes.

The BigchainDB core dev team develops BigchainDB on recent Ubuntu and Fedora distributions, so we recommend you use one of those. BigchainDB Server doesn't work on Windows and Mac OS X (unless you use a VM or containers).


## Option A: Using a Local Dev Machine

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


## Option B: Using a Dev Machine on Cloud9

Ian Worrall of [Encrypted Labs](http://www.encryptedlabs.com/) wrote a document (PDF) explaining how to set up a BigchainDB (Server) dev machine on [Cloud9](https://c9.io/):

[Download that document from GitHub](https://github.com/bigchaindb/bigchaindb/raw/master/docs/source/_static/cloud9.pdf)


## Option C: Using a Local Dev Machine and Docker

You need to have recent versions of [docker engine](https://docs.docker.com/engine/installation/#installation)
and [docker-compose](https://docs.docker.com/compose/install/).

Build the images:

```bash
docker-compose build
```

Start RethinkDB:

```bash
docker-compose up -d rdb
```

The RethinkDB web interface should be accessible at <http://localhost:58080/>.
Depending on which platform, and/or how you are running docker, you may need
to change `localhost` for the `ip` of the machine that is running docker. As a
dummy example, if the `ip` of that machine was `0.0.0.0`, you would accees the
web interface at: <http://0.0.0.0:58080/>.

Start a BigchainDB node:

```bash
docker-compose up -d bdb
```

You can monitor the logs:

```bash
docker-compose logs -f bdb
```

If you wish to run the tests:

```bash
docker-compose run --rm bdb py.test -v -n auto
```

A quick check to make sure that the BigchainDB server API is operational:

```bash
curl $(docker-compose port bdb 9984)
```

should give you something like:

```bash
{
  "api_endpoint": "http://bdb:9984/api/v1",
  "keyring": [],
  "public_key": "Brx8g4DdtEhccsENzNNV6yvQHR8s9ebhKyXPFkWUXh5e",
  "software": "BigchainDB",
  "version": "0.6.0"
}
```
How does the above curl command work? Inside the Docker container, BigchainDB
exposes the HTTP API on port `9984`. First we get the public port where that
port is bound:

```bash
docker-compose port bdb 9984
```

The port binding will change whenever you stop/restart the `bdb` service. You
should get an output similar to:

```bash
0.0.0.0:32772
```

but with a port different from `32772`.


Knowing the public port we can now perform a simple `GET` operation against the
root:

```bash
curl 0.0.0.0:32772
```
