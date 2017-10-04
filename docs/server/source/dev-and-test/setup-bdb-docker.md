# Set Up BigchainDB Node Using Docker

You need to have recent versions of [Docker](https://docs.docker.com/engine/installation/)
and (Docker) [Compose](https://docs.docker.com/compose/install/).

Build the images:

```bash
docker-compose build
```
## Docker with MongoDB

Start MongoDB:

```bash
docker-compose up -d mdb
```

MongoDB should now be up and running. You can check the port binding for the
MongoDB driver port using:
```bash
$ docker-compose port mdb 27017
```

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
docker-compose run --rm bdb py.test -v --database-backend=mongodb
```
## Docker with RethinkDB

**Note**: If you're upgrading BigchainDB and have previously already built the images, you may need
to rebuild them after the upgrade to install any new dependencies.

Start RethinkDB:

```bash
docker-compose -f docker-compose.rdb.yml up -d rdb
```

The RethinkDB web interface should be accessible at http://localhost:58080/.
Depending on which platform, and/or how you are running docker, you may need
to change `localhost` for the `ip` of the machine that is running docker. As a
dummy example, if the `ip` of that machine was `0.0.0.0`, you would access the
web interface at: http://0.0.0.0:58080/.

Start a BigchainDB node:

```bash
docker-compose -f docker-compose.rdb.yml up -d bdb-rdb
```

You can monitor the logs:

```bash
docker-compose -f docker-compose.rdb.yml logs -f bdb-rdb
```

If you wish to run the tests:

```bash
docker-compose -f docker-compose.rdb.yml run --rm bdb-rdb pytest -v -n auto
```

## Accessing the HTTP API

You can do quick check to make sure that the BigchainDB server API is operational:

```bash
curl $(docker-compose port bdb 9984)
```

The result should be a JSON object (inside braces like { })
containing the name of the software ("BigchainDB"),
the version of BigchainDB, the node's public key, and other information.

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
