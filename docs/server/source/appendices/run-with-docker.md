# Run BigchainDB with Docker

**NOT for Production Use**

For those who like using Docker and wish to experiment with BigchainDB in
non-production environments, we currently maintain a Docker image and a
`Dockerfile` that can be used to build an image for `bigchaindb`.

## Pull and Run the Image from Docker Hub

Assuming you have Docker installed, you would proceed as follows.

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
  --volume "$HOME/bigchaindb_docker:/data" \
  bigchaindb/bigchaindb \
  -y configure \
  [mongodb|rethinkdb]

Generating keypair
Configuration written to /data/.bigchaindb
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
 documentation](https://docs.docker.com/engine/tutorials/dockervolumes/#/mount-a-host-directory-as-a-data-volume)
* `bigchaindb/bigchaindb` the image to use. All the options after the container name are passed on to the entrypoint inside the container.
* `-y configure` execute the `configure` sub-command (of the `bigchaindb`
 command) inside the container, with the `-y` option to automatically use all the default config values
* `mongodb` or `rethinkdb` specifies the database backend to use with bigchaindb


### Run the backend database
From v0.9 onwards, you can run either RethinkDB or MongoDB.

We use the virtual interface created by the Docker daemon to allow
communication between the BigchainDB and database containers.
It has an IP address of 172.17.0.1 by default.

You can also use docker host networking or bind to your primary (eth)
 interface, if needed.

#### For RethinkDB

```text
docker run \
  --detach \
  --name=rethinkdb \
  --publish=172.17.0.1:28015:28015 \
  --publish=172.17.0.1:58080:8080 \
  rethinkdb:2.3
```


You can also access the RethinkDB dashboard at
[http://localhost:58080/](http://localhost:58080/)


#### For MongoDB

```text
docker run \
  --detach \
  --name=mongodb \
  --publish=172.17.0.1:27017:27017 \
  mongo:3.4.1 --replSet=bigchain-rs
```

### Run BigchainDB

```text
docker run \
  --detach \
  --name=bigchaindb \
  --publish=59984:9984 \
  --volume=$HOME/bigchaindb_docker:/data \
  bigchaindb/bigchaindb \
  start
```

The command is slightly different from the previous one, the differences are:

* `--detach` run the container in the background
* `--name bigchaindb` give a nice name to the container so it's easier to
 refer to it later
* `--publish "59984:9984"` map the host port `59984` to the container port `9984`
 (the BigchainDB API server)
* `start` start the BigchainDB service

Another way to publish the ports exposed by the container is to use the `-P` (or
`--publish-all`) option. This will publish all exposed ports to random ports. You can
always run `docker ps` to check the random mapping.

If that doesn't work, then replace `localhost` with the IP or hostname of the
machine running the Docker engine. If you are running docker-machine (e.g. on
Mac OS X) this will be the IP of the Docker machine (`docker-machine ip
machine_name`).

### Load Testing with Docker

Now that we have BigchainDB running in the Docker container named `bigchaindb`, we can
start another BigchainDB container to generate a load test for it.

First, make sure the container named `bigchaindb` is still running. You can check that using:
```text
docker ps
```

You should see a container named `bigchaindb` in the list.

You can load test the BigchainDB running in that container by running the `bigchaindb load` command in a second container:

```text
docker run \
  --env BIGCHAINDB_DATABASE_HOST=bigchaindb \
  --link bigchaindb \
  --rm \
  --volume "$HOME/bigchaindb_docker:/data" \
  bigchaindb/bigchaindb \
  load
```

Note the `--link` option to link to the first container (named `bigchaindb`).

Aside: The `bigchaindb load` command has several options (e.g. `-m`). You can read more about it in [the documentation about the BigchainDB command line interface](../server-reference/bigchaindb-cli.html).

If you look at the RethinkDB dashboard (in your web browser), you should see the effects of the load test. You can also see some effects in the Docker logs using:
```text
docker logs -f bigchaindb
```

## Building Your Own Image

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
