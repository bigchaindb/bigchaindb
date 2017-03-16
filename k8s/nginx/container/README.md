## Custom Nginx container for a Node

### Need

*  Since, BigchainDB and MongoDB both need to expose ports to the outside
   world (inter and intra cluster), we need to have a basic DDoS mitigation
   strategy to ensure that we can provide proper uptime and security these
   core services.

*  We can have a proxy like nginx/haproxy) in every node that listens to
   global connections and applies cluster level entry policy.

### Implementation
*  For MongoDB cluster communication, we will use nginx with a whitelist of
   IPs/FQDN of all the exising instances in the MongoDB cluster.
   replica set so as to allow connections from the whitelist and avoid a DDoS.

*  For BigchainDB connections, nginx needs to have rules to throttle
   connections that are throttle connections using resources over a threshold.


### Step 1: Build the Latest Container

Run `docker build -t bigchaindb/nginx .` from this folder.

Optional: Upload container to Docker Hub:
`docker push bigchaindb/nginx:latest`

### Step 2: Run the Container

```
docker run \
--env "MONGODB_FRONTEND_PORT=17017" \
--env "MONGODB_BACKEND_HOST=mdb-svc" \
--env "MONGODB_BACKEND_PORT=27017" \
--env "BIGCHAINDB_FRONTEND_PORT=80" \
--env "BIGCHAINDB_BACKEND_HOST=bdb-svc" \
--env "BIGCHAINDB_BACKEND_PORT=9984" \
--env "MONGODB_WHITELIST=95.91.241.60/16:192.168.0.1/16" \
--name=ngx \
--publish=80:80 \
--rm=true \
bigchaindb/nginx

```

