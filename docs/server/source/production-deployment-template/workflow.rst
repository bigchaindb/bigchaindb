Overview
========

This page summarizes the steps *we* go through
to set up a production BigchainDB cluster.
We are constantly improving them.
You can modify them to suit your needs.


Things the Managing Organization Must Do First
----------------------------------------------


1. Set Up a Self-Signed Certificate Authority
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We use SSL/TLS and self-signed certificates
for MongoDB authentication (and message encryption).
The certificates are signed by the organization managing the cluster.
If your organization already has a process
for signing certificates
(i.e. an internal self-signed certificate authority [CA]),
then you can skip this step.
Otherwise, your organization must
:ref:`set up its own self-signed certificate authority <How to Set Up a Self-Signed Certificate Authority>`.


2. Register a Domain and Get an SSL Certificate for It
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The BigchainDB APIs (HTTP API and WebSocket API) should be served using TLS,
so the organization running the cluster
should choose an FQDN for their API (e.g. api.organization-x.com),
register the domain name,
and buy an SSL/TLS certificate for the FQDN.


Things Each Node Operator Must Do
---------------------------------

☐ Every MongoDB instance in the cluster must have a unique (one-of-a-kind) name.
Ask the organization managing your cluster if they have a standard
way of naming instances in the cluster.
For example, maybe they assign a unique number to each node,
so that if you're operating node 12, your MongoDB instance would be named
``mdb-instance-12``.
Similarly, other instances must also have unique names in the cluster.
 
#. Name of the MongoDB instance (``mdb-instance-*``)
#. Name of the BigchainDB instance (``bdb-instance-*``)
#. Name of the NGINX instance (``ngx-http-instance-*`` or ``ngx-https-instance-*``)
#. Name of the OpenResty instance (``openresty-instance-*``)
#. Name of the MongoDB monitoring agent instance (``mdb-mon-instance-*``)
#. Name of the MongoDB backup agent instance (``mdb-bak-instance-*``)


☐ Generate four keys and corresponding certificate signing requests (CSRs):

#. Server Certificate (a.k.a. Member Certificate) for the MongoDB instance
#. Client Certificate for BigchainDB Server to identify itself to MongoDB
#. Client Certificate for MongoDB Monitoring Agent to identify itself to MongoDB
#. Client Certificate for MongoDB Backup Agent to identify itself to MongoDB

Ask the managing organization to use its self-signed CA to sign those four CSRs.
They should send you:

* Four certificates (one for each CSR you sent them).
* One ``ca.crt`` file: their CA certificate.
* One ``crl.pem`` file: a certificate revocation list.

For help, see the pages:

* :ref:`How to Generate a Server Certificate for MongoDB`
* :ref:`How to Generate a Client Certificate for MongoDB`


☐ Every node in a BigchainDB cluster needs its own
BigchainDB keypair (i.e. a public key and corresponding private key).
You can generate a BigchainDB keypair for your node, for example,
using the `BigchainDB Python Driver <http://docs.bigchaindb.com/projects/py-driver/en/latest/index.html>`_.

.. code:: python
        
   from bigchaindb_driver.crypto import generate_keypair
   print(generate_keypair())


☐ Share your BigchaindB *public* key with all the other nodes
in the BigchainDB cluster.
Don't share your private key.


☐ Get the BigchainDB public keys of all the other nodes in the cluster.
That list of public keys is known as the BigchainDB "keyring."


☐ Make up an FQDN for your BigchainDB node (e.g. ``mynode.mycorp.com``).
Make sure you've registered the associated domain name (e.g. ``mycorp.com``),
and have an SSL certificate for the FQDN.
(You can get an SSL certificate from any SSL certificate provider.)


☐ Ask the managing organization
for the FQDN used to serve the BigchainDB APIs
(e.g. ``api.orgname.net`` or ``bdb.clustername.com``)
and for a copy of the associated SSL/TLS certificate.
Also, ask for the user name to use for authenticating to MongoDB.


☐ If the cluster uses 3scale for API authentication, monitoring and billing,
you must ask the managing organization for all relevant 3scale credentials.


☐ If the cluster uses MongoDB Cloud Manager for monitoring and backup,
you must ask the managing organization for the ``Group ID`` and the
``Agent API Key``.
(Each Cloud Manager "group" has its own ``Group ID``. A ``Group ID`` can
contain a number of ``Agent API Key`` s. It can be found under
**Settings - Group Settings**. It was recently added to the Cloud Manager to
allow easier periodic rotation of the ``Agent API Key`` with a constant
``Group ID``)


☐ :doc:`Deploy a Kubernetes cluster on Azure <template-kubernetes-azure>`.


☐ You can now proceed to set up your BigchainDB node based on whether it is the
:ref:`first node in a new cluster
<Kubernetes Template: Deploy a Single BigchainDB Node>` or a
:ref:`node that will be added to an existing cluster
<Kubernetes Template: Add a BigchainDB Node to an Existing BigchainDB Cluster>`.
