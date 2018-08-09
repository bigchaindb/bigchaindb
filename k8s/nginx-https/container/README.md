<!---
Copyright BigchainDB GmbH and BigchainDB contributors
SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
Code is Apache-2.0 and docs are CC-BY-4.0
--->

## Nginx container for Secure WebSocket Support


### Step 1: Build and Push the Latest Container
Use the `docker_build_and_push.bash` script to build the latest docker image
and upload it to Docker Hub.
Ensure that the image tag is updated to a new version number to properly
reflect any changes made to the container.


### Note about testing Websocket connections:
You can test the WebSocket server by using
[wsc](https://www.npmjs.com/package/wsc) tool with a command like:

`wsc -er wss://localhost:9985/api/v1/streams/valid_transactions`.
