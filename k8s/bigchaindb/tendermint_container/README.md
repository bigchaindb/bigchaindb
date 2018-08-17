<!---
Copyright BigchainDB GmbH and BigchainDB contributors
SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
Code is Apache-2.0 and docs are CC-BY-4.0
--->

## Tendermint container used for BFT replication and consensus


### Step 1: Build and Push the Latest Container
Use the `docker_build_and_push.bash` script to build the latest docker image
and upload it to Docker Hub.
Ensure that the image tag is updated to a new version number to properly
reflect any changes made to the container.

### Step 2: Run the container

```
docker run \
  --name=tendermint \
  --env TM_PUB_KEY_ACCESS_PORT=<port to access public keys hosted by nginx> \
  --env TM_PERSISTENT_PEERS=<commad separated list of all peers IP addresses/Hostnames> \
  --env TM_VALIDATOR_POWER=<voting power of node> \
  --env TM_VALIDATORS=<list of all validators> \
  --env TM_GENESIS_TIME=<genesis time> \
  --env TM_CHAIN_ID=<chain id> \
  --env TM_P2P_PORT=<Port used by all peers to communicate> \
  --env TMHOME=<Tendermint home directory containing all config files> \
  --env TM_PROXY_APP=<Hostname/IP address of app> \
  --publish=<rpc port on host>:<rpc port> \
  --publish=<p2p port on host>:<p2p port> \
  --volume <host dir for tendermint data>:/tendermint \
  --volume=<host dir for public key>:/tendermint_node_data \
  bigchaindb/tendermint:<version_number>
```
