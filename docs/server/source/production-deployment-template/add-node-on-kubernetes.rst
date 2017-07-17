Kubernetes Template: Add a BigchainDB Node to an Existing BigchainDB Cluster
============================================================================

This page describes how to deploy a BigchainDB node using Kubernetes,
and how to add that node to an existing BigchainDB cluster.
It assumes you already have a running Kubernetes cluster
where you can deploy the new BigchainDB node.

If you want to deploy the first BigchainDB node in a BigchainDB cluster,
or a stand-alone BigchainDB node,
then see :doc:`the page about that <node-on-kubernetes>`.


Terminology Used
----------------

``existing cluster`` will refer to one of the existing Kubernetes clusters
hosting one of the existing BigchainDB nodes.

``ctx-1`` will refer to the kubectl context of the existing cluster.

``new cluster`` will refer to the new Kubernetes cluster that will run a new
BigchainDB node (including a BigchainDB instance and a MongoDB instance).

``ctx-2`` will refer to the kubectl context of the new cluster.

``new MongoDB instance`` will refer to the MongoDB instance in the new cluster.

``existing MongoDB instance`` will refer to the MongoDB instance in the
existing cluster.

``new BigchainDB instance`` will refer to the BigchainDB instance in the new
cluster.

``existing BigchainDB instance`` will refer to the BigchainDB instance in the
existing cluster.


Step 1: Prerequisites
---------------------

* A public/private key pair for the new BigchainDB instance.

* The public key should be shared offline with the other existing BigchainDB
  nodes in the existing BigchainDB cluster.

* You will need the public keys of all the existing BigchainDB nodes.

* A new Kubernetes cluster setup with kubectl configured to access it.

* Some familiarity with deploying a BigchainDB node on Kubernetes.
  See our :doc:`other docs about that <node-on-kubernetes>`.

Note: If you are managing multiple Kubernetes clusters, from your local
system, you can run ``kubectl config view`` to list all the contexts that
are available for the local kubectl.
To target a specific cluster, add a ``--context`` flag to the kubectl CLI. For
example:

.. code:: bash

   $ kubectl --context ctx-1 apply -f example.yaml
   $ kubectl --context ctx-2 apply -f example.yaml
   $ kubectl --context ctx-1 proxy --port 8001
   $ kubectl --context ctx-2 proxy --port 8002


Step 2: Prepare the New Kubernetes Cluster
------------------------------------------

Follow the steps in the sections to set up Storage Classes and Persistent Volume
Claims, and to run MongoDB in the new cluster:

1. :ref:`Add Storage Classes <Step 10: Create Kubernetes Storage Classes for MongoDB>`.
2. :ref:`Add Persistent Volume Claims <Step 11: Create Kubernetes Persistent Volume Claims>`.
3. :ref:`Create the Config Map <Step 3: Configure Your BigchainDB Node>`.
4. :ref:`Run MongoDB instance <Step 12: Start a Kubernetes StatefulSet for MongoDB>`.


Step 3: Add the New MongoDB Instance to the Existing Replica Set
----------------------------------------------------------------

Note that by ``replica set``, we are referring to the MongoDB replica set,
not a Kubernetes' ``ReplicaSet``.

If you are not the administrator of an existing BigchainDB node, you
will have to coordinate offline with an existing administrator so that they can
add the new MongoDB instance to the replica set.

Add the new instance of MongoDB from an existing instance by accessing the
``mongo`` shell.

.. code:: bash
   
   $ kubectl --context ctx-1 exec -it mdb-0 -c mongodb -- /bin/bash
   root@mdb-0# mongo --port 27017

One can only add members to a replica set from the ``PRIMARY`` instance.
The ``mongo`` shell prompt should state that this is the primary member in the
replica set.
If not, then you can use the ``rs.status()`` command to find out who the
primary is and login to the ``mongo`` shell in the primary.

Run the ``rs.add()`` command with the FQDN and port number of the other instances:

.. code:: bash

   PRIMARY> rs.add("<fqdn>:<port>")


Step 4: Verify the Replica Set Membership
-----------------------------------------

You can use the ``rs.conf()`` and the ``rs.status()`` commands available in the
mongo shell to verify the replica set membership.

The new MongoDB instance should be listed in the membership information
displayed.


Step 5: Start the New BigchainDB Instance
-----------------------------------------

Get the file ``bigchaindb-dep.yaml`` from GitHub using:

.. code:: bash

   $ wget https://raw.githubusercontent.com/bigchaindb/bigchaindb/master/k8s/bigchaindb/bigchaindb-dep.yaml

Note that we set the ``BIGCHAINDB_DATABASE_HOST`` to ``mdb`` which is the name
of the MongoDB service defined earlier.

Edit the ``BIGCHAINDB_KEYPAIR_PUBLIC`` with the public key of this instance,
the ``BIGCHAINDB_KEYPAIR_PRIVATE`` with the private key of this instance and
the ``BIGCHAINDB_KEYRING`` with a ``:`` delimited list of all the public keys
in the BigchainDB cluster.

Create the required Deployment using:

.. code:: bash

   $ kubectl --context ctx-2 apply -f bigchaindb-dep.yaml

You can check its status using the command ``kubectl get deploy -w``


Step 6: Restart the Existing BigchainDB Instance(s)
---------------------------------------------------

Add the public key of the new BigchainDB instance to the keyring of all the
existing BigchainDB instances and update the BigchainDB instances using:

.. code:: bash

   $ kubectl --context ctx-1 replace -f bigchaindb-dep.yaml 

This will create a "rolling deployment" in Kubernetes where a new instance of
BigchainDB will be created, and if the health check on the new instance is
successful, the earlier one will be terminated. This ensures that there is
zero downtime during updates.

You can SSH to an existing BigchainDB instance and run the ``bigchaindb
show-config`` command to check that the keyring is updated.


Step 7: Run NGINX as a Deployment
---------------------------------

Please see :ref:`this page <Step 9: Start the NGINX Kubernetes Deployment>` to
set up NGINX in your new node.


Step 8: Test Your New BigchainDB Node
-------------------------------------

Please refer to the testing steps :ref:`here <Step 19: Verify the BigchainDB
Node Setup>` to verify that your new BigchainDB node is working as expected.

