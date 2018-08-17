<!---
Copyright BigchainDB GmbH and BigchainDB contributors
SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
Code is Apache-2.0 and docs are CC-BY-4.0
--->

## Custom MongoDB container for BigchainDB Backend

### Step 1: Build and Push the Latest Container
Use the `docker_build_and_push.bash` script to build the latest docker image
and upload it to Docker Hub.
Ensure that the image tag is updated to a new version number to properly
reflect any changes made to the container.


### Step 2: Run the Container

```
docker run \
  --cap-add=FOWNER \
  --name=mdb1 \
  --publish=<mongo port number for external connections>:<corresponding host port> \
  --rm=true \
  --volume=<host dir for mongodb data files>:/data/db \
  --volume=<host dir for mongodb config data files>:/data/configdb \
  --volume=<host dir with the required TLS certificates>:/mongo-ssl:ro \
  bigchaindb/mongodb:<version of container> \
  --mongodb-port <mongod port number for external connections> \
  --mongodb-key-file-path /mongo-ssl/<private key file name>.pem \
  --mongodb-ca-file-path /mongo-ssl/<ca certificate file name>.crt \
  --mongodb-crl-file-path /mongo-ssl/<crl certificate file name>.pem \
  --mongodb-fqdn <fully qualified domain name of this instance> \
  --mongodb-ip <ip address of the mongodb container>
```
