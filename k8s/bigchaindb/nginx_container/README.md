<!---
Copyright BigchainDB GmbH and BigchainDB contributors
SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
Code is Apache-2.0 and docs are CC-BY-4.0
--->

## Nginx container for hosting public key for a tendermint instance


### Step 1: Build and Push the Latest Container
Use the `docker_build_and_push.bash` script to build the latest docker image
and upload it to Docker Hub.
Ensure that the image tag is updated to a new version number to properly
reflect any changes made to the container.

### Step 2: Run the container

```
docker run \
  --name=tendermint_instance_pub_key \
  --env TM_PUB_KEY_ACCESS_PORT=''
  --publish=<nginx port for external connections>:<corresponding host port> \
  --volume=<host dir with public key>:/usr/share/nginx \
  bigchaindb/nginx_pub_key_access:<version_number>
```
