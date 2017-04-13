# Production Node Components

A production BigchainDB node must include:

* BigchainDB Server
* MongoDB Server 3.4+ (mongod)
* Scalable storage for MongoDB

It could also include several other components, including:

* NGINX or similar, to provide authentication, rate limiting, etc.
* An NTP daemon running on all machines running BigchainDB Server or mongod, and possibly other machines
* **Not** MongoDB Automation Agent. It's for automating the deployment of an entire MongoDB cluster, not just one MongoDB node within a cluster.
* MongoDB Monitoring Agent
* MongoDB Backup Agent
* Log aggregation software
* Monitoring software
* Maybe more

The relationship between the main components is illustrated below. Note that BigchainDB Server must be able to communicate with the _primary_ MongoDB instance, and any of the MongoDB instances might be the primary, so BigchainDB Server must be able to communicate with all the MongoDB instances. Also, all MongoDB instances must be able to communicate with each other.

![Components of a production node](../_static/Node-components.png)
