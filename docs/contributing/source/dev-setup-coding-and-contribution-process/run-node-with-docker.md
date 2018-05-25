# Run BigchainDB with Docker

**NOT for Production Use**

For those who like using Docker and wish to experiment with BigchainDB in
non-production environments, we currently maintain a Docker image and a
`Dockerfile` that can be used to build an image for `bigchaindb`.

## Prerequisite(s)
- [Docker](https://docs.docker.com/engine/installation/)

## Pull and Run the Image from Docker Hub

With Docker installed, you can proceed as follows.

In a terminal shell, pull the latest version of the BigchainDB Docker image using:
```text
docker pull bigchaindb/bigchaindb
```

### Configuration
A one-time configuration step is required to create the config file; we will use
the `-y` option to accept all the default values. The configuration file will
be stored in a file on your host machine at `~/bigchaindb_docker/.bigchaindb`:

```text
docker run \
  --interactive \
  --rm \
  --tty \
  --volume $HOME/bigchaindb_docker:/data \
  --env BIGCHAINDB_DATABASE_HOST=172.17.0.1 \
  bigchaindb/bigchaindb \
  -y configure \
  localmongodb

Generating default configuration for backend localmongodb
Configuration written to /root/.bigchaindb
Ready to go!
```

Let's analyze that command:

* `docker run` tells Docker to run some image
* `--interactive` keep STDIN open even if not attached
* `--rm` remove the container once we are done
* `--tty` allocate a pseudo-TTY
* `--volume "$HOME/bigchaindb_docker:/data"` map the host directory
 `$HOME/bigchaindb_docker` to the container directory `/data`;
 this allows us to have the data persisted on the host machine,
 you can read more in the [official Docker
 documentation](https://docs.docker.com/engine/tutorials/dockervolumes)
* `--env BIGCHAINDB_DATABASE_HOST=172.17.0.1`, `172.17.0.1` is the default `docker0` bridge
IP address, for fresh Docker installations. It is used for the communication between BigchainDB and database
containers.
* `bigchaindb/bigchaindb` the image to use. All the options after the container name are passed on to the entrypoint inside the container.
* `-y configure` execute the `configure` sub-command (of the `bigchaindb`
 command) inside the container, with the `-y` option to automatically use all the default config values
* `localmongodb` specifies the database backend to use with bigchaindb


### Run the backend database

BigchainDB v2.0 only supports MongoDB as a backend database.

You can also use docker host networking or bind to your primary (eth)
 interface, if needed.

```text
docker run \
  --detach \
  --name=mongodb \
  --publish=27017:27017 \
  --restart=always \
  --volume=$HOME/mongodb_docker/db:/data/db \
  --volume=$HOME/mongodb_docker/configdb:/data/configdb \
  mongo:3.4.13
```

### Run BigchainDB

```text
docker run \
  --detach \
  --name=bigchaindb \
  --publish=9984:9984 \
  --publish=9985:9985 \
  --publish=46658:46658 \
  --restart=always \
  --env BIGCHAINDB_TENDERMINT_HOST=172.17.0.1 \
  --volume=$HOME/bigchaindb_docker:/data \
  bigchaindb/bigchaindb \
  start
```

The command is slightly different from the previous one, the differences are:

* `--detach` run the container in the background
* `--name bigchaindb` give a nice name to the container so it's easier to
 refer to it later
* `--publish "9984:9984"` map the host port `9984` to the container port `9984`
 (the BigchainDB API server)
* `--publish "9985:9985"` map the host port `9985` to the container port `9985`
 (the BigchainDB Websocket server)
* `--publish "46658:46658"` map the host port `46658` to the container port `46658`
 (Tendermint ABCI)
* `start` start the BigchainDB service

Another way to publish the ports exposed by the container is to use the `-P` (or
`--publish-all`) option. This will publish all exposed ports to random ports. You can
always run `docker ps` to check the random mapping.

If that doesn't work, then replace `localhost` with the IP or hostname of the
machine running the Docker engine. If you are running docker-machine (e.g. on
Mac OS X) this will be the IP of the Docker machine (`docker-machine ip
machine_name`).

### Run Tendermint

Tendermint is the consensus backend used by BigchainDB to become Byzantine
Fault Tolerant.

```text
docker run \
  --detach \
  --name=tendermint \
  --publish=46656:46656 \
  --publish=46657:46657 \
  --restart=always \
  --volume=$HOME/tendermint_docker/tendermint:/tendermint \
  --env TMHOME=/tendermint \
  --entrypoint "/bin/sh" \
  tendermint/tendermint:0.19.2 \
  -c "tendermint init && tendermint unsafe_reset_all && \
  tendermint node --consensus.create_empty_blocks=false \
  --proxy_app=tcp://172.17.0.1:46658"
```

