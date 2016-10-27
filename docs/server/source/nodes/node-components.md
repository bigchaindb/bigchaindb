# Production Node Components

A BigchainDB node must include, at least:

* BigchainDB Server and
* RethinkDB Server.

When doing development and testing, it's common to install both on the same machine, but in a production environment, it may make more sense to install them on separate machines.

In a production environment, a BigchainDB node should have several other components, including:

* nginx or similar, as a reverse proxy and/or load balancer for the Gunicorn server(s) inside the node
* An NTP daemon running on all machines running BigchainDB code, and possibly other machines
* A RethinkDB proxy server
* A RethinkDB "wire protocol firewall" (in the future: this component doesn't exist yet)
* Scalable storage for RethinkDB (e.g. using RAID)
* Monitoring software, to monitor all the machines in the node
* Configuration management agents (if you're using a configuration managment system that uses agents)
* Maybe more

The relationship between these components is illustrated below.

![Components of a node](../_static/Node-components.png)
