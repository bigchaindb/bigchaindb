# Run BigchainDB with Docker On Mac

**NOT for Production Use**

Those hacking on Mac can follow this document to run BigchainDB.
Running BigchainDB on Mac(Docker or otherwise) is not officially supported
currently.

## Prerequisite

Install Docker for Mac.

## (Optional) For a clean start

1.  Stop all BigchainDB and RethinkDB/MongoDB containers.
2.  Delete all BigchainDB docker images.
3.  Delete the ~/bigchaindb_docker folder.


## Pull the images

Pull the bigchaindb and other required docker images from docker hub.

```text
docker pull bigchaindb/bigchaindb:master
docker pull [rethinkdb:2.3|mongo:3.4.1]
```

## Create the BigchainDB configuration file on Mac
```text
docker run \
  --rm \
  --volume $HOME/bigchaindb_docker:/data \
  bigchaindb/bigchaindb:master \
  -y configure \
  [mongodb|rethinkdb]
```

To ensure that BigchainDB connects to the backend database bound to the virtual
interface `172.17.0.1`, you must edit the BigchainDB configuration file
(`~/bigchaindb_docker/.bigchaindb`) and change database.host from `localhost`
to `172.17.0.1`.


## Run the backend database on Mac

From v0.9 onwards, you can run RethinkDB or MongoDB.

We use the virtual interface created by the Docker daemon to allow
communication between the BigchainDB and database containers.
It has an IP address of 172.17.0.1 by default.

You can also use docker host networking or bind to your primary (eth)
interface, if needed.

### For RethinkDB backend
```text
docker run \
  --name=rethinkdb \
  --publish=28015:28015 \
  --publish=8080:8080 \
  --restart=always \
  --volume $HOME/bigchaindb_docker:/data \
  rethinkdb:2.3
```

### For MongoDB backend
```text
docker run \
  --name=mongodb \
  --publish=27017:27017 \
  --restart=always \
  --volume=$HOME/bigchaindb_docker/db:/data/db \
  --volume=$HOME/bigchaindb_docker/configdb:/data/configdb \
  mongo:3.4.1 --replSet=bigchain-rs
```

### Run BigchainDB on Mac
```text
docker run \
  --name=bigchaindb \
  --publish=9984:9984 \
  --restart=always \
  --volume=$HOME/bigchaindb_docker:/data \
  bigchaindb/bigchaindb \
  start
```

