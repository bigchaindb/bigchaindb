# Deploying a Local Multi-Node RethinkDB Cluster

This section explains one way to deploy a multi-node RethinkDB cluster on one machine. You could use such a cluster as a storage backend for a BigchaindB process running on that machine.

## Launching More RethinkDB Nodes

Assuming you've already [installed RethinkDB](installing-server.html#install-and-run-rethinkdb-server) and have one RethinkDB node running, here's how you can launch two more nodes on the same machine. First, prepare two additional nodes. Note that the user who starts RethinkDB must have write access to the created directories:

    mkdir -p /path/to/node2
    mkdir -p /path/to/node3

then launch two more nodes:

    rethinkdb --port-offset 1 --directory /path/to/node2 --join localhost:29015
    rethinkdb --port-offset 2 --directory /path/to/node3 --join localhost:29015

You should now have a three-node RethinkDB cluster up and running. You should be able to monitor it at [http://localhost:8080](http://localhost:8080).

Note: if you play around with replication, the number of transactions will increase. For the real throughput, you should divide the number of transactions by the number of replicas.

## Securing the Cluster

We have turned on the `bind=all` option for connecting other nodes and making RethinkDB accessible from outside the server. Unfortunately, that is insecure, so we need to block access to the RethinkDB cluster from the Internet. At the same time, we need to allow access to its services from authorized computers.

For the cluster port, we will use a firewall to enclose our cluster. For the web management console and the driver port, we will use SSH tunnels to access them from outside the server. SSH tunnels redirect requests on a client computer to a remote computer over SSH, giving the client access to all of the services only available on the remote server's localhost name space.

Repeat the following steps on all your RethinkDB servers.

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

Save the `iptables` config:

    sudo apt-get update
    sudo apt-get install iptables-persistent

You can find out more about `iptables` in the [man pages](http://linux.die.net/man/8/iptables).

## Troubleshooting

You can get help with RethinkDB from [RethinkDB experts](https://rethinkdb.com/services/) and [the RethinkDB community](https://rethinkdb.com/community/).

If your nodes in a sharded and replicated cluster are not in sync, it may help if you delete the data of the affected node and restart the node. If there are no other problems, your node will come back and sync within a couple of minutes. You can verify this by monitoring the cluster via the monitoring url: [http://localhost:8080](http://localhost:8080).
