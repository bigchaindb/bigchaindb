.. _how-to-configure-a-bigchaindb-node:

How to Configure a BigchainDB Node
==================================

This page outlines the steps to set a bunch of configuration settings
in your BigchainDB node.
They are pushed to the Kubernetes cluster in two files,
named ``config-map.yaml`` (a set of ConfigMaps)
and ``secret.yaml`` (a set of Secrets).
They are stored in the Kubernetes cluster's key-value store (etcd).

Make sure you did all the things listed in the section titled
:ref:`things-each-node-operator-must-do`
(including generation of all the SSL certificates needed
for MongoDB auth).


Edit config-map.yaml
--------------------

Make a copy of the file ``k8s/configuration/config-map.yaml``
and edit the data values in the various ConfigMaps.
That file already contains many comments to help you
understand each data value, but we make some additional
remarks on some of the values below.

Note: None of the data values in ``config-map.yaml`` need
to be base64-encoded. (This is unlike ``secret.yaml``,
where all data values must be base64-encoded.
This is true of all Kubernetes ConfigMaps and Secrets.)


vars.cluster-fqdn
~~~~~~~~~~~~~~~~~

The ``cluster-fqdn`` field specifies the domain you would have
:ref:`registered before <register-a-domain-and-get-an-ssl-certificate-for-it>`.


vars.cluster-frontend-port
~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``cluster-frontend-port`` field specifies the port on which your cluster
will be available to all external clients.
It is set to the HTTPS port ``443`` by default.


vars.cluster-health-check-port
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``cluster-healthcheck-port`` is the port number on which health check
probes are sent to the main NGINX instance.
It is set to ``8888`` by default.


vars.cluster-dns-server-ip
~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``cluster-dns-server-ip`` is the IP of the DNS server for a node.
We use DNS for service discovery. A Kubernetes deployment always has a DNS
server (``kube-dns``) running at 10.0.0.10, and since we use Kubernetes, this is
set to ``10.0.0.10`` by default, which is the default ``kube-dns`` IP address.


vars.mdb-instance-name and Similar
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Your BigchainDB cluster organization should have a standard way
of naming instances, so the instances in your BigchainDB node
should conform to that standard (i.e. you can't just make up some names).
There are some things worth noting about the ``mdb-instance-name``:

* This field will be the DNS name of your MongoDB instance, and Kubernetes
  maps this name to its internal DNS.
* We use ``mdb-instance-0``, ``mdb-instance-1`` and so on in our
  documentation. Your BigchainDB cluster may use a different naming convention.


vars.ngx-mdb-instance-name and Similar
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

NGINX needs the FQDN of the servers inside the cluster to be able to forward
traffic.
The ``ngx-openresty-instance-name``, ``ngx-mdb-instance-name`` and
``ngx-bdb-instance-name`` are the FQDNs of the OpenResty instance, the MongoDB
instance, and the BigchainDB instance in this Kubernetes cluster respectively.
In Kubernetes, this is usually the name of the module specified in the
corresponding ``vars.*-instance-name`` followed by the
``<namespace name>.svc.cluster.local``. For example, if you run OpenResty in
the default Kubernetes namespace, this will be
``<vars.openresty-instance-name>.default.svc.cluster.local``


vars.mongodb-frontend-port and vars.mongodb-backend-port
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``mongodb-frontend-port`` is the port number on which external clients can
access MongoDB. This needs to be restricted to only other MongoDB instances
by enabling an authentication mechanism on MongoDB cluster.
It is set to ``27017`` by default.

The ``mongodb-backend-port`` is the port number on which MongoDB is actually
available/listening for requests in your cluster.
It is also set to ``27017`` by default.


vars.openresty-backend-port
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``openresty-backend-port`` is the port number on which OpenResty is
listening for requests.
This is used by the NGINX instance to forward requests
destined for the OpenResty instance to the right port.
This is also used by OpenResty instance to bind to the correct port to
receive requests from NGINX instance.
It is set to ``80`` by default.


vars.bigchaindb-wsserver-advertised-scheme
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``bigchaindb-wsserver-advertised-scheme`` is the protocol used to access
the WebSocket API in BigchainDB. This can be set to ``wss`` or ``ws``.
It is set to ``wss`` by default.


vars.bigchaindb-api-port, vars.bigchaindb-ws-port and Similar
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``bigchaindb-api-port`` is the port number on which BigchainDB is
listening for HTTP requests. Currently set to ``9984`` by default.

The ``bigchaindb-ws-port`` is the port number on which BigchainDB is
listening for Websocket requests. Currently set to ``9985`` by default.

There's another :doc:`page with a complete listing of all the BigchainDB Server
configuration settings <../server-reference/configuration>`.


bdb-config.bdb-user
~~~~~~~~~~~~~~~~~~~

This is the user name that BigchainDB uses to authenticate itself to the
backend MongoDB database.

We need to specify the user name *as seen in the certificate* issued to
the BigchainDB instance in order to authenticate correctly. Use
the following ``openssl`` command to extract the user name from the
certificate:

.. code:: bash

   $ openssl x509 -in <path to the bigchaindb certificate> \
     -inform PEM -subject -nameopt RFC2253

You should see an output line that resembles:

.. code:: bash

   subject= emailAddress=dev@bigchaindb.com,CN=test-bdb-ssl,OU=BigchainDB-Instance,O=BigchainDB GmbH,L=Berlin,ST=Berlin,C=DE

The ``subject`` line states the complete user name we need to use for this
field (``bdb-config.bdb-user``), i.e.

.. code:: bash

   emailAddress=dev@bigchaindb.com,CN=test-bdb-ssl,OU=BigchainDB-Instance,O=BigchainDB GmbH,L=Berlin,ST=Berlin,C=DE


tendermint-config.tm-instance-name
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Your BigchainDB cluster organization should have a standard way
of naming instances, so the instances in your BigchainDB node
should conform to that standard. There are some things worth noting
about the ``tm-instance-name``:

* This field will be the DNS name of your Tendermint instance, and Kubernetes
  maps this name to its internal DNS, so all the peer to peer communication
  depends on this, in case of a network/multi-node deployment.
* This parameter is also used to access the public key of a particular node.
* We use ``tm-instance-0``, ``tm-instance-1`` and so on in our
  documentation. Your BigchainDB cluster may use a different naming convention.


tendermint-config.ngx-tm-instance-name
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

NGINX needs the FQDN of the servers inside the cluster to be able to forward
traffic.
``ngx-tm-instance-name`` is the FQDN of the Tendermint
instance in this Kubernetes cluster.
In Kubernetes, this is usually the name of the module specified in the
corresponding ``tendermint-config.*-instance-name`` followed by the
``<namespace name>.svc.cluster.local``. For example, if you run Tendermint in
the default Kubernetes namespace, this will be
``<tendermint-config.tm-instance-name>.default.svc.cluster.local``


tendermint-config.tm-seeds
~~~~~~~~~~~~~~~~~~~~~~~~~~

``tm-seeds`` is the initial set of peers to connect to. It is a comma separated
list of all the peers part of the cluster.

If you are deploying a stand-alone BigchainDB node the value should the same as
``<tm-instance-name>``. If you are deploying a network this parameter will look
like this:

.. code::

    <tm-instance-1>,<tm-instance-2>,<tm-instance-3>,<tm-instance-4>


tendermint-config.tm-validators
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``tm-validators`` is the initial set of validators in the network. It is a comma separated list
of all the participant validator nodes.

If you are deploying a stand-alone BigchainDB node the value should be the same as
``<tm-instance-name>``. If you are deploying a network this parameter will look like
this:

.. code::

    <tm-instance-1>,<tm-instance-2>,<tm-instance-3>,<tm-instance-4>


tendermint-config.tm-validator-power
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``tm-validator-power`` represents the voting power of each validator. It is a comma separated
list of all the participants in the network.

**Note**: The order of the validator power list should be the same as the ``tm-validators`` list.

.. code::

    tm-validators: <tm-instance-1>,<tm-instance-2>,<tm-instance-3>,<tm-instance-4>

For the above list of validators the ``tm-validator-power`` list should look like this:

.. code::

    tm-validator-power: <tm-instance-1-power>,<tm-instance-2-power>,<tm-instance-3-power>,<tm-instance-4-power>


tendermint-config.tm-genesis-time
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``tm-genesis-time`` represents the official time of blockchain start. Details regarding, how to generate
this parameter are covered :ref:`here <generate-the-blockchain-id-and-genesis-time>`.


tendermint-config.tm-chain-id
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``tm-chain-id`` represents the ID of the blockchain. This must be unique for every blockchain.
Details regarding, how to generate this parameter are covered
:ref:`here <generate-the-blockchain-id-and-genesis-time>`.


tendermint-config.tm-abci-port
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``tm-abci-port`` has a default value ``46658`` which is used by Tendermint Core for
ABCI(Application BlockChain Interface) traffic. BigchainDB nodes use this port
internally to communicate with Tendermint Core.


tendermint-config.tm-p2p-port
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``tm-p2p-port`` has a default value ``46656`` which is used by Tendermint Core for
peer to peer communication.

For a multi-node/zone deployment, this port needs to be available publicly for P2P
communication between Tendermint nodes.


tendermint-config.tm-rpc-port
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``tm-rpc-port`` has a default value ``46657`` which is used by Tendermint Core for RPC
traffic. BigchainDB nodes use this port with RPC listen address.


tendermint-config.tm-pub-key-access
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``tm-pub-key-access`` has a default value ``9986``, which is used to discover the public
key of a tendermint node. Each Tendermint StatefulSet(Pod, Tendermint + NGINX) hosts its
public key.

.. code::

  http://tendermint-instance-1:9986/pub_key.json


Edit secret.yaml
----------------

Make a copy of the file ``k8s/configuration/secret.yaml``
and edit the data values in the various Secrets.
That file includes many comments to explain the required values.
**In particular, note that all values must be base64-encoded.**
There are tips at the top of the file
explaining how to convert values into base64-encoded values.

Your BigchainDB node might not need all the Secrets.
For example, if you plan to access the BigchainDB API over HTTP, you
don't need the ``https-certs`` Secret.
You can delete the Secrets you don't need,
or set their data values to ``""``.

Note that ``ca.pem`` is just another name for ``ca.crt``
(the certificate of your BigchainDB cluster's self-signed CA).


threescale-credentials.*
~~~~~~~~~~~~~~~~~~~~~~~~

If you're not using 3scale,
you can delete the ``threescale-credentials`` Secret
or leave all the values blank (``""``).

If you *are* using 3scale, get the values for ``secret-token``,
``service-id``, ``version-header`` and ``service-token`` by logging in to 3scale
portal using your admin account, click **APIs** and click on **Integration**
for the relevant API.
Scroll to the bottom of the page and click the small link
in the lower right corner, labelled **Download the NGINX Config files**.
Unzip it(if it is a ``zip`` file). Open the ``.conf`` and the ``.lua`` file.
You should be able to find all the values in those files.
You have to be careful because it will have values for **all** your APIs,
and some values vary from API to API.
The ``version-header`` is the timestamp in a line that looks like:

.. code::

    proxy_set_header  X-3scale-Version "2017-06-28T14:57:34Z";


Deploy Your config-map.yaml and secret.yaml
-------------------------------------------

You can deploy your edited ``config-map.yaml`` and ``secret.yaml``
files to your Kubernetes cluster using the commands:

.. code:: bash

   $ kubectl apply -f config-map.yaml

   $ kubectl apply -f secret.yaml
