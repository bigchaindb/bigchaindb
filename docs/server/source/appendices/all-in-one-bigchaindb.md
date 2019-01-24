<!---
Copyright BigchainDB GmbH and BigchainDB contributors
SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
Code is Apache-2.0 and docs are CC-BY-4.0
--->

# Run BigchainDB with all-in-one Docker

For those who like using Docker and wish to experiment with BigchainDB in
non-production environments, we currently maintain a BigchainDB all-in-one 
Docker image and a
`Dockerfile-all-in-one` that can be used to build an image for `bigchaindb`.

This image contains all the services required for a BigchainDB node i.e.

- BigchainDB Server
- MongoDB
- Tendermint

**Note:** **NOT for Production Use:** *This is an single node opinionated image not well suited for a network deployment.*
*This image is to help quick deployment for early adopters, for a more standard approach please refer to one of our deployment guides:*

- [BigchainDB developer setup guides](https://docs.bigchaindb.com/projects/contributing/en/latest/dev-setup-coding-and-contribution-process/index.html).
- [BigchainDB with Kubernetes](http://docs.bigchaindb.com/projects/server/en/latest/k8s-deployment-template/index.html).

## Prerequisite(s)
- [Docker](https://docs.docker.com/engine/installation/)

## Pull and Run the Image from Docker Hub

With Docker installed, you can proceed as follows.

In a terminal shell, pull the latest version of the BigchainDB all-in-one Docker image using:
```text
$ docker pull bigchaindb/bigchaindb:all-in-one

$ docker run \
  --detach \
  --name bigchaindb \
  --publish 9984:9984 \
  --publish 9985:9985 \
  --publish 27017:27017 \
  --publish 26657:26657 \
  --volume $HOME/bigchaindb_docker/mongodb/data/db:/data/db \
  --volume $HOME/bigchaindb_docker/mongodb/data/configdb:/data/configdb \
  --volume $HOME/bigchaindb_docker/tendermint:/tendermint \
  bigchaindb/bigchaindb:all-in-one
```

Let's analyze that command:

* `docker run` tells Docker to run some image
* `--detach` run the container in the background
* `publish 9984:9984` map the host port `9984` to the container port `9984`
 (the BigchainDB API server) 
  * `9985` BigchainDB Websocket server
  * `27017` Default port for MongoDB
  * `26657` Tendermint RPC server
* `--volume "$HOME/bigchaindb_docker/mongodb:/data"` map the host directory
 `$HOME/bigchaindb_docker/mongodb` to the container directory `/data`;
 this allows us to have the data persisted on the host machine,
 you can read more in the [official Docker
 documentation](https://docs.docker.com/engine/tutorials/dockervolumes)
  * `$HOME/bigchaindb_docker/tendermint:/tendermint` to persist Tendermint data.
* `bigchaindb/bigchaindb:all-in-one` the image to use. All the options after the container name are passed on to the entrypoint inside the container.

## Verify

```text
$ docker ps | grep bigchaindb
```

Send your first transaction using [BigchainDB drivers](../drivers-clients/index).


## Building Your Own Image

Assuming you have Docker installed, you would proceed as follows.

In a terminal shell:
```text
git clone git@github.com:bigchaindb/bigchaindb.git
cd bigchaindb/
```

Build the Docker image:
```text
docker build --file Dockerfile-all-in-one --tag <tag/name:latest> .
```

Now you can use your own image to run BigchainDB all-in-one container.
