Add a BigchainDB Node in a Kubernetes Cluster
=============================================

**Refer this document if you want to add a new BigchainDB node to an existing
cluster**

**If you want to start your first BigchainDB node in the BigchainDB cluster,
refer**
:doc:`this <node-on-kubernetes>`


Terminology Used
----------------

``existing cluster`` will refer to the existing (or any one of the existing)
Kubernetes cluster that already hosts a BigchainDB instance with a MongoDB
backend.

``ctx-1`` will refer to the kubectl context of the existing cluster.

``new cluster`` will refer to the new Kubernetes cluster that will run a new
BigchainDB instance with a MongoDB backend.

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

* You will need to have a public and private key for the new BigchainDB
  instance you will set up.

* The public key should be shared offline with the other existing BigchainDB
  instances. The means to achieve this requirement is beyond the scope of this
  document.

* You will need the public keys of all the existing BigchainDB instances. The
  means to achieve this requirement is beyond the scope of this document.

* A new Kubernetes cluster setup with kubectl configured to access it.
  If you are using Kubernetes on Azure Container Server (ACS), please refer
  our documentation `here <template-kubernetes-azure>` for the set up.

If you haven't read our guide to set up a
:doc:`node on Kubernetes <node-on-kubernetes>`, now is a good time to jump in
there and then come back here as these instructions build up from there.


NOTE: If you are managing multiple kubernetes clusters, from your local
system, you can run ``kubectl config view`` to list all the contexts that
are available for the local kubectl.
To target a specific cluster, add a ``--context`` flag to the kubectl CLI. For
example:

.. code:: bash

   $ kubectl --context ctx-1 apply -f example.yaml
   $ kubectl --context ctx-2 apply -f example.yaml
   $ kubectl --context ctx-1 proxy --port 8001
   $ kubectl --context ctx-2 proxy --port 8002


Step 2: Prepare the New Kubernetes cluster
------------------------------------------
Follow the steps in the sections to set up Storage Classes and Persisten Volume
Claims, and to run MongoDB in the new cluster:

1. :ref:`Add Storage Classes <Step 3: Create Storage Classes>`
2. :ref:`Add Persistent Volume Claims <Step 4: Create Persistent Volume Claims>`
3. :ref:`Create the Config Map <Step 5: Create the Config Map - Optional>`
4. :ref:`Run MongoDB instance <Step 6: Run MongoDB as a StatefulSet>`


Step 3: Add the New MongoDB Instance to the Existing Replica Set
----------------------------------------------------------------
Note that by ``replica set`` we are referring to the MongoDB replica set, and not
to Kubernetes' ``ReplicaSet``.

If you are not the administrator of an existing MongoDB/BigchainDB instance, you
will have to coordinate offline with an existing administrator so that s/he can
add the new MongoDB instance to the replica set. The means to achieve this is
beyond the scope of this document.

Add the new instance of MongoDB from an existing instance by accessing the
``mongo`` shell.

.. code:: bash
   
   $ kubectl --context ctx-1 exec -it mdb-0 -c mongodb -- /bin/bash
   root@mdb-0# mongo --port 27017

We can only add members to a replica set from the ``PRIMARY`` instance.
The ``mongo`` shell prompt should state that this is the primary member in the
replica set.
If not, then you can use the ``rs.status()`` command to find out who the
primary is and login to the ``mongo`` shell in the primary.

Run the ``rs.add()`` command with the FQDN and port number of the other instances:

.. code:: bash

   PRIMARY> rs.add("<fqdn>:<port>")


Step 4: Verify the replica set membership
-----------------------------------------

You can use the ``rs.conf()`` and the ``rs.status()`` commands available in the
mongo shell to verify the replica set membership.

The new MongoDB instance should be listed in the membership information
displayed.


Step 5: Start the new BigchainDB instance
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


Step 6: Restart the existing BigchainDB instance(s)
---------------------------------------------------
Add public key of the new BigchainDB instance to the keyring of all the
existing instances and update the BigchainDB instances using:

.. code:: bash

   $ kubectl --context ctx-1 replace -f bigchaindb-dep.yaml 

This will create a ``rolling deployment`` in Kubernetes where a new instance of
BigchainDB will be created, and if the health check on the new instance is
successful, the earlier one will be terminated. This ensures that there is
zero downtime during updates.

You can login to an existing BigchainDB instance and run the ``bigchaindb
show-config`` command to see the configuration update to the keyring.

