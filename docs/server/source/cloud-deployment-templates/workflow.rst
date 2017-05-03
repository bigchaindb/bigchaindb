Setup a Production Node
=======================


Step 1: One Off Setup - Done by the Federation
----------------------------------------------

This step is usually done by a central authority before deciding to set up a
federation.

This involves setting up a self-signed CA for signing certificates used for
securing the MongoDB cluster.


Step 1.1: Setup a Self-Signed CA
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

See the page on how to
:ref:`set up a self-signed CA <Setup a Self-Signed Certificate Authority>`.


Step 2: Setup a Federation Node
-------------------------------

Step 2.1: Get proper credentials to start or join an existing federation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This step can include sharing your node's public keys with other existing nodes
and getting the public keys of all the other nodes.

If you are setting up the first node in the cluster, you need be generate the
public and private keys for this node.

One way to generate keys for your node is using the BigchinDB Python driver.

    .. code:: bash
        
        from bigchaindb_driver.crypto import generate_keypair
        print(generate_keypair())


Step 2.2: Get the HTTPS Certificates for the BigchainDB API
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

TODO(Troy): How to get certificates from certificate providers? Out of scope?
Suggestions here?


Step 2.3: Get the TLS Certificates to Secure MongoDB Cluster
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you are the admin of the federation with access to the CA, you can generate a
server and a client certificate for providing secure authentication between the
BigchainDB and MongoDB instances, as well as between different MongoDB
instances in the cluster.

If you are not the admin, then you might have to request the federation admin
to sign your certificates.

In total, you will need to generate 4 keys and corresponding CSRs for:

#. Server Certificate or Member Certificate for MongoDB
#. Client Certificate for BigchainDB
#. Client Certificate for MongoDB Monitoring Agent
#. Client Certificate for MongoDB Backup Agent

One way to generate server and client certificates and the corresponding CSRs
can be found :ref:`here <Generate Cluster Member Certificate for MongoDB>`
and :ref:`here <Generate Client Certificate for MongoDB>`.


Step 2.3: Get 3scale API Gateway Account credentials
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This helps you set up auth, monitoring and billing of your APIs

TODO(Troy): How to setup an account?
TODO(Krish): How to get all the credentials from the portal?


Step 2.4: Get the API keys from MongoDB Cloud Manager
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This helps to monitor and backup the MongoDB cluster in your node.

#. Log in the the MongoDB Cloud Manager and select the group that will monitor
   and backup this cluster from the dropdown box.

#. Go to Settings, Group Settings and copy the ``Agent Api Key``.


Step 2.5: Other common configuration options
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

#. Name of the mongodb instance (``mdb-instance-*``)
#. Name of the bigchaindb instance (``bdb-instance-*``)
#. Name of the nginx instance (``ngx-instance-*``)
#. Name of the monitoring and backup agent instances (``mdb-mon-instance-*`` and ``mdb-bak-instance-*``)
#. FQDN of the node for which the HTTPS certificates were issued in step 2.2
   above.


Step 3: Create a Kubernetes Cluster on Azure
--------------------------------------------

If this is your first node in the federation, see
:ref:`this <First Node or Bootstrap Node Setup>` page on how to set it up.


Step 4: Create the Kubernetes Configuration for this Node
---------------------------------------------------------

We will use Kubernetes ConfigMap and Secrets to hold all the information
gathered above.



