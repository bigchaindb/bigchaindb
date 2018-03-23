# Setup development environment

## Setting up a single node development environment with ``docker-compose``

You can also use [Docker Compose](https://docs.docker.com/compose/) to run all the tests.

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
