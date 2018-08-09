<!---
Copyright BigchainDB GmbH and BigchainDB contributors
SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
Code is Apache-2.0 and docs are CC-BY-4.0
--->

# Notes on Running a Local Dev Node with Docker Compose

## Setting up a single node development environment with ``docker-compose``

### Using the BigchainDB 2.0 developer toolbox
We grouped all useful commands under a simple `Makefile`.

Run a BigchainDB node in the foreground:
```bash
$ make run
```

There are also other commands you can execute:
- `make start`: Run BigchainDB from source and daemonize it (stop it with `make stop`).
- `make stop`: Stop BigchainDB.
- `make logs`: Attach to the logs.
- `make test`: Run all unit and acceptance tests.
- `make test-unit-watch`: Run all tests and wait. Every time you change code, tests will be run again.
- `make cov`: Check code coverage and open the result in the browser.
- `make doc`: Generate HTML documentation and open it in the browser.
- `make clean`: Remove all build, test, coverage and Python artifacts.
- `make reset`: Stop and REMOVE all containers. WARNING: you will LOSE all data stored in BigchainDB.


### Using `docker-compose` directly
The BigchainDB `Makefile` is a wrapper around some `docker-compose` commands we use frequently. If you need a finer granularity to manage the containers, you can still use `docker-compose` directly. This part of the documentation explains how to do that.

```bash
$ docker-compose build bigchaindb
$ docker-compose up -d bdb
```

The above command will launch all 3 main required services/processes:

* ``mongodb``
* ``tendermint``
* ``bigchaindb``

To follow the logs of the ``tendermint`` service:

```bash
$ docker-compose logs -f tendermint
```

To follow the logs of the ``bigchaindb`` service:

```bash
$ docker-compose logs -f bigchaindb
```

To follow the logs of the ``mongodb`` service:

```bash
$ docker-compose logs -f mdb
```

Simple health check:

```bash
$ docker-compose up curl-client
```

Post and retrieve a transaction -- copy/paste a driver basic example of a
``CREATE`` transaction:

```bash
$ docker-compose -f docker-compose.yml run --rm bdb-driver ipython
```

**TODO**: A python script to post and retrieve a transaction(s).

### Running Tests

Run all the tests using:

```bash
$ docker-compose run --rm --no-deps bigchaindb pytest -v
```

Run tests from a file:

```bash
$ docker-compose run --rm --no-deps bigchaindb pytest /path/to/file -v
```

Run specific tests:
```bash
$ docker-compose run --rm --no-deps bigchaindb pytest /path/to/file -k "<test_name>" -v
```

### Building Docs

You can also develop and build the BigchainDB docs using ``docker-compose``:

```bash
$ docker-compose build bdocs
$ docker-compose up -d bdocs
```

The docs will be hosted on port **33333**, and can be accessed over [localhost](http:/localhost:33333), [127.0.0.1](http:/127.0.0.1:33333)
OR http:/HOST_IP:33333.
