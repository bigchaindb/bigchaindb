## Custom MongoDB container for BigchainDB Backend

### Need

*  MongoDB needs the hostname provided in the `rs.initiate()` command to be
   resolvable through the hosts file locally.
*  In the future, with the introduction of TLS for inter-cluster MongoDB
   communications, we will need a way to specify detailed configuration.
*  We also need a way to overwrite certain parameters to suit our use case.


### Step 1: Build the Latest Container

`docker build -t bigchaindb/mongodb:3.4.4 .` from the root of this project.


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
  bigchaindb/mongodb:3.4.4 \
  --mongodb-port <mongod port number for external connections> \
  --mongodb-key-file-path /mongo-ssl/<private key file name>.pem \
  --mongodb-key-file-password <password for the private key file> \
  --mongodb-ca-file-path /mongo-ssl/<ca certificate file name>.crt \
  --mongodb-crl-file-path /mongo-ssl/<crl certificate file name>.pem \
  --replica-set-name <replica set name> \
  --mongodb-fqdn <fully qualified domain name of this instance> \
  --mongodb-ip <ip address of the mongodb container>
```

#### Step 3: Initialize the Replica Set

Login to one of the MongoDB containers, say mdb1:

`docker exec -it mongodb bash`

Since we need TLS certificates to use the mongo shell now, copy them using:

```
docker cp bdb-instance-0.pem mongodb:/
docker cp ca.crt mongodb:/
```

Start the `mongo` shell:

```
mongo --host mdb1-fqdn --port mdb1-port --verbose --ssl \
  --sslCAFile /ca.crt \
  --sslPEMKeyFile /bdb-instance-0.pem \
  --sslPEMKeyPassword password
```

Run the rs.initiate() command:
```
rs.initiate({ 
  _id : "<replica-set-name", members: [
  { 
    _id : 0,
    host : "<fqdn of this instance>:<port number>"
  } ]
})
```

For example:

```
rs.initiate({ _id : "test-repl-set", members: [ { _id : 0, host :
"mdb-instance-0.westeurope.cloudapp.azure.com:27017" } ] })
```

You should also see changes in the mongo shell prompt from `>` to
`test-repl-set:OTHER>` to `test-repl-set:SECONDARY>` to finally
`test-repl-set:PRIMARY>`.
If this instance is not the primary, you can use the `rs.status()` command to
find out who is the primary.


#### Step 4: Add members to the Replica Set

We can only add members to a replica set from the PRIMARY instance.
Login to the PRIMARY and open a `mongo` shell.

Run the rs.add() command with the ip and port number of the other
containers/instances:
```
rs.add("<fqdn>:<port>")
```

For example:

Add mdb2 to replica set from mdb1:
```
rs.add("bdb-cluster-1.northeurope.cloudapp.azure.com:27017")
```

Add mdb3 to replica set from mdb1:
```
rs.add("bdb-cluster-2.northeurope.cloudapp.azure.com:27017")
```

