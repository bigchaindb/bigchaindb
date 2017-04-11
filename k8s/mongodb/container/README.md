## Custom MongoDB container for BigchainDB Backend

### Need

*  MongoDB needs the hostname provided in the rs.initiate() command to be
   resolvable through the hosts file locally.
*  In the future, with the introduction of TLS for inter-cluster MongoDB
   communications, we will need a way to specify detailed configuration.
*  We also need a way to overwrite certain parameters to suit our use case.


### Step 1: Build the Latest Container

`make` from the root of this project.


### Step 2: Run the Container

```
docker run \
--name=mdb1 \
--publish=<mongo port number for external connections>:<corresponding host port> \
--rm=true \
bigchaindb/mongodb \
--replica-set-name <replica set name> \
--fqdn <fully qualified domain name of this instance> \
--port <mongod port number for external connections>
```

#### Step 3: Initialize the Replica Set

Login to one of the MongoDB containers, say mdb1:

`docker exec -it mdb1 bash`

Start the `mongo` shell:

`mongo --port 27017`


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

