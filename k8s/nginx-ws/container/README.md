## Nginx container for Secure WebSocket Support


### Step 1: Build and Push the Latest Container
Use the `docker_build_and_push.bash` script to build the latest docker image
and upload it to Docker Hub.
Ensure that the image tag is updated to a new version number to properly
reflect any changes made to the container.


### Step 2: Run the Container

Use the following CLI to run the container:
```
docker run \
    --env "BIGCHAINDB_WS_FRONTEND_PORT=<port where nginx listens for BigchainDB WebSocket connections>" \
    --env "BIGCHAINDB_BACKEND_HOST=<ip/hostname of instance where BigchainDB is running>" \
    --env "BIGCHAINDB_WS_BACKEND_PORT=<port where BigchainDB is listening for websocket connections>" \
    --env "DNS_SERVER=<ip of the dns server>" \
    --name=ngx \
    --publish=<port where nginx listens for BigchainDB WS connections as specified above>:<corresponding host port> \
    --rm=true \
    bigchaindb/nginx_ws:1.0
```

For example:
```
docker run \
  --env="BIGCHAINDB_WS_FRONTEND_PORT=81" \
  --env="BIGCHAINDB_BACKEND_HOST=localhost" \
  --env="BIGCHAINDB_WS_BACKEND_PORT=9985" \
  --env="DNS_SERVER=127.0.0.1" \
  --name=ngx \
  --publish=81:81 \
  --rm=true \
  bigchaindb/nginx_ws:1.0
```

### Note:
You can test the WebSocket server by using 
[wsc](https://www.npmjs.com/package/wsc) tool with a command like:
`wsc -er ws://localhost:9985/api/v1/streams/valid_tx`.
