
.. Copyright BigchainDB GmbH and BigchainDB contributors
   SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
   Code is Apache-2.0 and docs are CC-BY-4.0

Architecture of a BigchainDB Node Running in a Kubernetes Cluster
=================================================================

.. note::

   A highly-available Kubernetes cluster requires at least five virtual machines
   (three for the master and two for your app's containers).
   Therefore we don't recommend using Kubernetes to run a BigchainDB node
   if that's the only thing the Kubernetes cluster will be running.
   Instead, see our :ref:`simple-deployment-template`.
   If your organization already *has* a big Kubernetes cluster running many containers,
   and your organization has people who know Kubernetes,
   then this Kubernetes deployment template might be helpful.

If you deploy a BigchainDB node into a Kubernetes cluster
as described in these docs, it will include:

* NGINX, OpenResty, BigchainDB, MongoDB and Tendermint
  `Kubernetes Services <https://kubernetes.io/docs/concepts/services-networking/service/>`_.
* NGINX, OpenResty, BigchainDB and MongoDB Monitoring Agent
  `Kubernetes Deployments <https://kubernetes.io/docs/concepts/workloads/controllers/deployment/>`_.
* MongoDB and Tendermint `Kubernetes StatefulSets <https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/>`_.
* Third party services like `3scale <https://3scale.net>`_,
  `MongoDB Cloud Manager <https://cloud.mongodb.com>`_ and the
  `Azure Operations Management Suite
  <https://docs.microsoft.com/en-us/azure/operations-management-suite/>`_.


.. _bigchaindb-node:

BigchainDB Node
---------------

.. aafig::
  :aspect: 60
  :scale: 100
  :background: #rgb
  :proportional:

                                                              +            +
  +--------------------------------------------------------------------------------------------------------------------------------------+
  |                                                           |            |                                                             |
  |                                                           |            |                                                             |
  |                                                           |            |                                                             |
  |                                                           |            |                                                             |
  |                                                           |            |                                                             |
  |                                                           |            |                                                             |
  |                                         "BigchainDB API"  |            |  "Tendermint P2P"                                           |
  |                                                           |            |  "Communication/"                                           |
  |                                                           |            |  "Public Key Exchange"                                      |
  |                                                           |            |                                                             |
  |                                                           |            |                                                             |
  |                                                           v            v                                                             |
  |                                                                                                                                      |
  |                                                          +------------------+                                                        |
  |                                                          |"NGINX Service"   |                                                        |
  |                                                          +-------+----------+                                                        |
  |                                                                  |                                                                   |
  |                                                                  v                                                                   |
  |                                                                                                                                      |
  |                                                          +------------------+                                                        |
  |                                                          |   "NGINX"        |                                                        |
  |                                                          |   "Deployment"   |                                                        |
  |                                                          |                  |                                                        |
  |                                                          +-------+----------+                                                        |
  |                                                                  |                                                                   |
  |                                                                  |                                                                   |
  |                                                                  |                                                                   |
  |                                                                  v                                                                   |
  |                                                                                                                                      |
  |                                      "443"                   +----------+         "26656/9986"                                       |
  |                                                              | "Rate"   |                                                            |
  |                                  +---------------------------+"Limiting"+-----------------------+                                    |
  |                                  |                           | "Logic"  |                       |                                    |
  |                                  |                           +----+-----+                       |                                    |
  |                                  |                                |                             |                                    |
  |                                  |                                |                             |                                    |
  |                                  |                                |                             |                                    |
  |                                  |                                |                             |                                    |
  |                                  |                                |                             |                                    |
  |                                  |                        "27017" |                             |                                    |
  |                                  v                                |                             v                                    |
  |                            +-------------+                        |                         +------------+                           |
  |                            |"HTTPS"      |                        |    +------------------> |"Tendermint"|                           |
  |                            |"Termination"|                        |    |            "9986"  |"Service"   |  "26656"                  |
  |                            |             |                        |    |            +-------+            | <----+                    |
  |                            +-----+-------+                        |    |            |       +------------+      |                    |
  |                                  |                                |    |            |                           |                    |
  |                                  |                                |    |            v                           v                    |
  |                                  |                                |    |        +------------+              +------------+           |
  |                                  |                                |    |        |"NGINX"     |              |"Tendermint"|           |
  |                                  |                                |    |        |"Deployment"|              |"Stateful"  |           |
  |                                  |                                |    |        |"Pub-Key-Ex"|              |"Set"       |           |
  |                                  ^                                |    |        +------------+              +------------+           |
  |                            +-----+-------+                        |    |                                                             |
  |                  "POST"    |"Analyze"    |  "GET"                 |    |                                                             |
  |                            |"Request"    |                        |    |                                                             |
  |                +-----------+             +--------+               |    |                                                             |
  |                |           +-------------+        |               |    |                                                             |
  |                |                                  |               |    | "Bi+directional, communication between"                     |
  |                |                                  |               |    | "BigchainDB(APP) and Tendermint"                            |
  |                |                                  |               |    | "BFT consensus Engine"                                      |
  |                |                                  |               |    |                                                             |
  |                v                                  v               |    |                                                             |
  |                                                                   |    |                                                             |
  |         +-------------+                 +--------------+          +----+------------------->  +--------------+                       |
  |         | "OpenResty" |                 | "BigchainDB" |               |                      |  "MongoDB"   |                       |
  |         | "Service"   |                 | "Service"    |               |                      |  "Service"   |                       |
  |         |             |          +----->|              |               |            +-------> |              |                       |
  |         +------+------+          |      +------+-------+               |            |         +------+-------+                       |
  |                |                 |             |                       |            |                 |                              |
  |                |                 |             |                       |            |                 |                              |
  |                v                 |             v                       |            |                 v                              |
  |          +-------------+         |        +-------------+              |            |            +----------+                        |
  |          |             |         |        |             | <------------+            |            |"MongoDB" |                        |
  |          |"OpenResty"  |         |        | "BigchainDB"|                           |            |"Stateful"|                        |
  |          |"Deployment" |         |        | "Deployment"|                           |            |"Set"     |                        |
  |          |             |         |        |             |                           |            +-----+----+                        |
  |          |             |         |        |             +---------------------------+                  |                             |
  |          |             |         |        |             |                                              |                             |
  |          +-----+-------+         |        +-------------+                                              |                             |
  |                |                 |                                                                     |                             |
  |                |                 |                                                                     |                             |
  |                v                 |                                                                     |                             |
  |           +-----------+          |                                                                     v                             |
  |           | "Auth"    |          |                                                              +------------+                       |
  |           | "Logic"   |----------+                                                              |"MongoDB"   |                       |
  |           |           |                                                                         |"Monitoring"|                       |
  |           |           |                                                                         |"Agent"     |                       |
  |           +---+-------+                                                                         +-----+------+                       |
  |               |                                                                                       |                              |
  |               |                                                                                       |                              |
  |               |                                                                                       |                              |
  |               |                                                                                       |                              |
  |               |                                                                                       |                              |
  |               |                                                                                       |                              |
  +---------------+---------------------------------------------------------------------------------------+------------------------------+
                  |                                                                                       |
                  |                                                                                       |
                  |                                                                                       |
                  v                                                                                       v
  +------------------------------------+                                                +------------------------------------+
  |                                    |                                                |                                    |
  |                                    |                                                |                                    |
  |                                    |                                                |                                    |
  |     "3Scale"                       |                                                |   "MongoDB Cloud"                  |
  |                                    |                                                |                                    |
  |                                    |                                                |                                    |
  |                                    |                                                |                                    |
  +------------------------------------+                                                +------------------------------------+




.. note::
  The arrows in the diagram represent the client-server communication. For
  example, A-->B implies that A initiates the connection to B.
  It does not represent the flow of data; the communication channel is always
  fully duplex.


NGINX: Entrypoint and Gateway
-----------------------------

We use an NGINX as HTTP proxy on port 443 (configurable) at the cloud
entrypoint for:

#. Rate Limiting: We configure NGINX to allow only a certain number of requests
   (configurable) which prevents DoS attacks.

#. HTTPS Termination: The HTTPS connection does not carry through all the way
   to BigchainDB and terminates at NGINX for now.

#. Request Routing: For HTTPS connections on port 443 (or the configured BigchainDB public api port),
   the connection is proxied to:

   #. OpenResty Service if it is a POST request.
   #. BigchainDB Service if it is a GET request.


We use an NGINX TCP proxy on port 27017 (configurable) at the cloud
entrypoint for:

#. Rate Limiting: We configure NGINX to allow only a certain number of requests
   (configurable) which prevents DoS attacks.

#. Request Routing: For connections on port 27017 (or the configured MongoDB
   public api port), the connection is proxied to the MongoDB Service.


OpenResty: API Management, Authentication and Authorization
-----------------------------------------------------------

We use `OpenResty <https://openresty.org/>`_ to perform authorization checks
with 3scale using the ``app_id`` and ``app_key`` headers in the HTTP request.

OpenResty is NGINX plus a bunch of other
`components <https://openresty.org/en/components.html>`_. We primarily depend
on the LuaJIT compiler to execute the functions to authenticate the ``app_id``
and ``app_key`` with the 3scale backend.


MongoDB: Standalone
-------------------

We use MongoDB as the backend database for BigchainDB.

We achieve security by avoiding DoS attacks at the NGINX proxy layer and by
ensuring that MongoDB has TLS enabled for all its connections.


Tendermint: BFT consensus engine
--------------------------------

We use Tendermint as the backend consensus engine for BFT replication of BigchainDB.
In a multi-node deployment, Tendermint nodes/peers communicate with each other via
the public ports exposed by the NGINX gateway.

We use port **9986** (configurable) to allow tendermint nodes to access the public keys
of the peers and port **26656** (configurable) for the rest of the communications between
the peers.

