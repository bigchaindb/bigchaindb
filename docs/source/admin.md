# Server/Cluster Deployment and Administration
This section covers everything which might concern a BigchainDB server/cluster administrator:
* deployment
* security
* monitoring
* troubleshooting



## Deploying a local cluster
One of the advantages of RethinkDB as the storage backend is the easy installation. Developers like to have everything locally, so let's install a local storage backend cluster from scratch.
Here is an example to run a cluster assuming rethinkdb is already [installed](installing.html#installing-and-running-rethinkdb-server-on-ubuntu-12-04) in
your system:

    # preparing two additional nodes
    # remember, that the user who starts rethinkdb must have write access to the paths
    mkdir -p /path/to/node2
    mkdir -p /path/to/node3

    # then start your additional nodes
    rethinkdb --port-offset 1 --directory /path/to/node2 --join localhost:29015
    rethinkdb --port-offset 2 --directory /path/to/node3 --join localhost:29015

That's all, folks! Cluster is up and running. Check it out in your browser at http://localhost:8080, which opens the console.

Now you can install BigchainDB and run it against the storage backend!

## Securing the storage backend
We have turned on the bind=all option for connecting other nodes and making RethinkDB accessible from outside the server. Unfortunately this is insecure. So, we will need to block RethinkDB off from the Internet. But we need to allow access to its services from authorized computers.

For the cluster port, we will use a firewall to enclose our cluster. For the web management console and the driver port, we will use SSH tunnels to access them from outside the server. SSH tunnels redirect requests on a client computer to a remote computer over SSH, giving the client access to all of the services only available on the remote server's localhost name space.

Repeat these steps on all your RethinkDB servers.

First, block all outside connections:

    # the web management console
    sudo iptables -A INPUT -i eth0 -p tcp --dport 8080 -j DROP
    sudo iptables -I INPUT -i eth0 -s 127.0.0.1 -p tcp --dport 8080 -j ACCEPT

    # the driver port
    sudo iptables -A INPUT -i eth0 -p tcp --dport 28015 -j DROP
    sudo iptables -I INPUT -i eth0 -s 127.0.0.1 -p tcp --dport 28015 -j ACCEPT

    # the communication port
    sudo iptables -A INPUT -i eth0 -p tcp --dport 29015 -j DROP
    sudo iptables -I INPUT -i eth0 -s 127.0.0.1 -p tcp --dport 29015 -j ACCEPT

Save the iptables config:

    sudo apt-get update
    sudo apt-get install iptables-persistent

More about iptables you can find in the [man pages](http://linux.die.net/man/8/iptables).

## Monitoring the storage backend
Monitoring is pretty simple. You can do this via the [monitoring url](http://localhost:8080). Here you see the complete behaviour of all nodes.
One annotation: if you play around with  replication the number of transaction will increase. So for the real throughput you should devide the number of transactions by the number of replicas.

## Troubleshooting
Since every software may have some minor issues we are not responsible for the storage backend.
If your nodes in a sharded and replicated cluster are not in sync, it may help if you delete the data of the affected node and restart the node. If there are no other problems your node will come back and sync within a couple of minutes. You can verify this by monitoring the cluster via the [monitoring url](http://localhost:8080).
