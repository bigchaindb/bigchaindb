## Custom Nginx container for a Node

### Need

*  Since, BigchainDB and MongoDB both need to expose ports to the outside
   world (inter and intra cluster), we need to have a basic DDoS mitigation
   strategy to ensure that we can provide proper uptime and security these
   core services.

*  We can have a proxy like nginx/haproxy in every node that listens to
   global connections and applies cluster level entry policy.

### Implementation
*  For BigchainDB connections, nginx needs to have rules to throttle
   connections that are using resources over a threshold.


### Step 1: Build and Push the Latest Container
Use the `docker_build_and_push.bash` script to build the latest docker image
and upload it to Docker Hub.
Ensure that the image tag is updated to a new version number to properly
reflect any changes made to the container.


### Step 2: Run the Container

Note that the whilelist IPs must be specified with the subnet in the CIDR
format, eg: `1.2.3.4/16` 

```
docker run \
    --env "MONGODB_FRONTEND_PORT=<port where nginx listens for MongoDB connections>" \
    --env "MONGODB_BACKEND_HOST=<ip/hostname of instance where MongoDB is running>" \
    --env "MONGODB_BACKEND_PORT=<port where MongoDB is listening for connections>" \
    --env "BIGCHAINDB_FRONTEND_PORT=<port where nginx listens for BigchainDB connections>" \
    --env "BIGCHAINDB_BACKEND_HOST=<ip/hostname of instance where BigchainDB is running>" \
    --env "BIGCHAINDB_BACKEND_PORT=<port where BigchainDB is listening for connections>" \
    --env "DNS_SERVER=<ip of the dns server>" \
    --name=ngx \
    --publish=<port where nginx listens for MongoDB connections as specified above>:<correcponding host port> \
    --publish=<port where nginx listens for BigchainDB connections as specified above>:<corresponding host port> \
    --rm=true \
    bigchaindb/nginx_api:1.0 
```

For example:
```
docker run \
  --env="MONGODB_FRONTEND_PORT=17017" \
  --env="MONGODB_BACKEND_HOST=localhost" \
  --env="MONGODB_BACKEND_PORT=27017" \
  --env="BIGCHAINDB_FRONTEND_PORT=80" \
  --env="BIGCHAINDB_BACKEND_HOST=localhost" \
  --env="BIGCHAINDB_BACKEND_PORT=9984" \
  --env="DNS_SERVER=127.0.0.1" \
  --name=ngx \
  --publish=80:80 \
  --publish=17017:17017 \
  --rm=true \
  bigchaindb/nginx_api:1.0 
```
