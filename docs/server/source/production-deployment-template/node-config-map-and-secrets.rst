How to Configure a BigchainDB Node
==================================

This page outlines the steps to set a bunch of configuration settings
in your BigchainDB node.
They are pushed to the Kubernetes cluster in two files,
named ``config-map.yaml`` (a set of ConfigMaps)
and ``secret.yaml`` (a set of Secrets).
They are stored in the Kubernetes cluster's key-value store (etcd).

Make sure you did all the things listed in the section titled
:ref:`Things Each Node Operator Must Do`
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
:ref:`registered before <2. Register a Domain and Get an SSL Certificate for It>`.


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

* MongoDB reads the local ``/etc/hosts`` file while bootstrapping a replica
  set to resolve the hostname provided to the ``rs.initiate()`` command.
  It needs to ensure that the replica set is being initialized in the same
  instance where the MongoDB instance is running.
* We use the value in the ``mdb-instance-name`` field to achieve this.
* This field will be the DNS name of your MongoDB instance, and Kubernetes
  maps this name to its internal DNS.
* This field will also be used by other MongoDB instances when forming a
  MongoDB replica set.
* We use ``mdb-instance-0``, ``mdb-instance-1`` and so on in our
  documentation. Your BigchainDB cluster may use a different naming convention.


vars.ngx-ndb-instance-name and Similar
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


vars.bigchaindb-api-port and vars.bigchaindb-ws-port
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``bigchaindb-api-port`` is the port number on which BigchainDB is
listening for HTTP requests. Currently set to ``9984`` by default.

The ``bigchaindb-ws-port`` is the port number on which BigchainDB is
listening for Websocket requests. Currently set to ``9985`` by default.


bdb-config.bdb-keyring
~~~~~~~~~~~~~~~~~~~~~~~

This lists the BigchainDB public keys
of all *other* nodes in your BigchainDB cluster
(not including the public key of your BigchainDB node). Cases:

* If you're deploying the first node in the cluster,
  the value should be ``""`` (an empty string).
* If you're deploying the second node in the cluster,
  the value should be the BigchainDB public key of the first/original
  node in the cluster.
  For example,
  ``"EPQk5i5yYpoUwGVM8VKZRjM8CYxB6j8Lu8i8SG7kGGce"``
* If there are two or more other nodes already in the cluster,
  the value should be a colon-separated list
  of the BigchainDB public keys
  of those other nodes.
  For example,
  ``"DPjpKbmbPYPKVAuf6VSkqGCf5jzrEh69Ldef6TrLwsEQ:EPQk5i5yYpoUwGVM8VKZRjM8CYxB6j8Lu8i8SG7kGGce"``

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
``service-id``, ``version-header`` and ``provider-key`` by logging in to 3scale
portal using your admin account, click **APIs** and click on **Integration**
for the relevant API.
Scroll to the bottom of the page and click the small link
in the lower right corner, labelled **Download the NGINX Config files**.
You'll get a ``.zip`` file.
Unzip it, then open the ``.conf`` file and the ``.lua`` file.
You should be able to find all the values in those files.
You have to be careful because it will have values for *all* your APIs,
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
