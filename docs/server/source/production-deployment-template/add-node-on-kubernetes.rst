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

Below, we refer to multiple files by their directory and filename,
such as ``mongodb/mongo-ext-conn-svc.yaml``. Those files are files in the
`bigchaindb/bigchaindb repository on GitHub
<https://github.com/bigchaindb/bigchaindb/>`_ in the ``k8s/`` directory.
Make sure you're getting those files from the appropriate Git branch on
GitHub, i.e. the branch for the version of BigchainDB that your BigchainDB
cluster is using.


Step 1: Prerequisites
---------------------

* A public/private key pair for the new BigchainDB instance.

* The public key should be shared offline with the other existing BigchainDB
  nodes in the existing BigchainDB cluster.

* You will need the public keys of all the existing BigchainDB nodes.

* Client Certificate for the new BigchainDB Server to identify itself to the cluster.

* A new Kubernetes cluster setup with kubectl configured to access it.

* Some familiarity with deploying a BigchainDB node on Kubernetes.
  See our :doc:`other docs about that <node-on-kubernetes>`.

* You will need a client certificate for each MongoDB monitoring and backup agent.

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
4. :ref:`Prepare the Kubernetes Secrets <Step 3: Configure Your BigchainDB Node>`, as per your
   requirement i.e. if you do not want a certain functionality, just remove it from the
   ``configuration/secret.yaml``.
5. :ref:`Run MongoDB instance <Step 12: Start a Kubernetes StatefulSet for MongoDB>`.


Step 3: Start NGINX service, Assign DNS to NGINX Pubic IP and run NGINX deployment
----------------------------------------------------------------------------------

Please see the following pages:

* :ref:`Start NGINX service <Step 4: Start the NGINX Service>`.
* :ref:`Assign DNS to NGINX Public IP <Step 5: Assign DNS Name to the NGINX Public IP>`.
* :ref:`Run NGINX deployment <Step 9: Start the NGINX Kubernetes Deployment>`.


Step 4: Verify network connectivity between the MongoDB instances
-----------------------------------------------------------------

Make sure your MongoDB instances can access each other over the network. *If* you are deploying
the new MongoDB node in a different cluster or geographical location using Azure Kubernetes Container
Service, you will have to set up networking between the two clusters using `Kubernetes
Services <https://kubernetes.io/docs/concepts/services-networking/service/>`_.

Assuming we have an existing MongoDB instance ``mdb-instance-0`` residing in Azure data center location ``westeurope`` and we
want to add a new MongoDB instance ``mdb-instance-1`` located in Azure data center location ``eastus`` to the existing MongoDB
replica set. Unless you already have explicitly set up networking for ``mdb-instance-0`` to communicate with ``mdb-instance-1`` and
vice versa, we will have to add a Kubernetes Service in each cluster to accomplish this goal in order to set up a
MongoDB replica set.

* This configuration is located in the file ``mongodb/mongo-ext-conn-svc.yaml``.

* Set the name of the ``metadata.name`` to the host name of the MongoDB instance you are trying to connect to.
  For instance if you are configuring this service on cluster with `mdb-instance-0` then the ``metadata.name`` will
  be ``mdb-instance-1`` and vice versa.

* Set ``spec.ports.port[0]`` to the ``mongodb-backend-port`` from the ConfigMap.

* Set ``spec.externalName`` to the FQDN mapped to NGINX Public IP of the cluster you are trying to connect to.
  For more information about the FQDN please refer to: :ref:`Assign DNS Name to the NGINX Public
  IP <Step 5: Assign DNS Name to the NGINX Public IP>`

.. note::
   This operation needs to be replicated ``n-1`` times per node for a ``n`` node cluster, with the respective FQDNs
   we need to communicate with.


Step 5: Add the New MongoDB Instance to the Existing Replica Set
----------------------------------------------------------------

Note that by ``replica set``, we are referring to the MongoDB replica set,
not a Kubernetes' ``ReplicaSet``.

If you are not the administrator of an existing BigchainDB node, you
will have to coordinate offline with an existing administrator so that they can
add the new MongoDB instance to the replica set.

Add the new instance of MongoDB from an existing instance by accessing the
``mongo`` shell and authenticate as the ``adminUser`` we created for existing MongoDB instance OR 
contact the admin of the PRIMARY MongoDB node:

.. code:: bash

   $ kubectl --context ctx-1 exec -it <existing-mongodb-host-name> -c mongodb -- /bin/bash
   $ mongo --host <existing-mongodb-host-name> --port 27017 --verbose --ssl \
     --sslCAFile /etc/mongod/ssl/ca.pem \
     --sslPEMKeyFile /etc/mongod/ssl/mdb-instance.pem

   PRIMARY> use admin
   PRIMARY> db.auth("adminUser", "superstrongpassword")

One can only add members to a replica set from the ``PRIMARY`` instance.
The ``mongo`` shell prompt should state that this is the primary member in the
replica set.
If not, then you can use the ``rs.status()`` command to find out who the
primary is and login to the ``mongo`` shell in the primary.

Run the ``rs.add()`` command with the FQDN and port number of the other instances:

.. code:: bash

   PRIMARY> rs.add("<fqdn>:<port>")


Step 6: Verify the Replica Set Membership
-----------------------------------------

You can use the ``rs.conf()`` and the ``rs.status()`` commands available in the
mongo shell to verify the replica set membership.

The new MongoDB instance should be listed in the membership information
displayed.


Step 7: Start the New BigchainDB Instance
-----------------------------------------

Get the file ``bigchaindb-dep.yaml`` from GitHub using:

.. code:: bash

   $ wget https://raw.githubusercontent.com/bigchaindb/bigchaindb/master/k8s/bigchaindb/bigchaindb-dep.yaml


* Set ``metadata.name`` and ``spec.template.metadata.labels.app`` to the
  value set in ``bdb-instance-name`` in the ConfigMap, followed by
  ``-dep``.
  For example, if the value set in the
  ``bdb-instance-name`` is ``bdb-instance-0``, set the fields to the
  value ``bdb-instance-0-dep``.

* Set the value of ``BIGCHAINDB_KEYPAIR_PRIVATE`` (not base64-encoded).
  (In the future, we'd like to pull the BigchainDB private key from
  the Secret named ``bdb-private-key``, but a Secret can only be mounted as a file,
  so BigchainDB Server would have to be modified to look for it
  in a file.)

* As we gain more experience running BigchainDB in testing and production,
  we will tweak the ``resources.limits`` values for CPU and memory, and as
  richer monitoring and probing becomes available in BigchainDB, we will
  tweak the ``livenessProbe`` and ``readinessProbe`` parameters.

* Set the ports to be exposed from the pod in the
  ``spec.containers[0].ports`` section. We currently expose 2 ports -
  ``bigchaindb-api-port`` and ``bigchaindb-ws-port``. Set them to the
  values specified in the ConfigMap.

* Uncomment the env var ``BIGCHAINDB_KEYRING``, it will pick up the
  ``:`` delimited list of all the public keys in the BigchainDB cluster from the ConfigMap.

* Authenticate the new BigchainDB instance using the client x.509 certificate with MongoDB. We need to specify the
  user name *as seen in the certificate* issued to the BigchainDB instance in order to authenticate correctly.
  Please refer to: :ref:`Configure Users and Access Control for MongoDB <Step 13: Configure Users and Access Control for MongoDB>`

Create the required Deployment using:

.. code:: bash

   $ kubectl --context ctx-2 apply -f bigchaindb-dep.yaml

You can check its status using the command ``kubectl get deploy -w``


Step 8: Restart the Existing BigchainDB Instance(s)
---------------------------------------------------

Add the public key of the new BigchainDB instance to the ConfigMap ``bdb-keyring``
variable of existing BigchainDB instances, update the ConfigMap of the existing
BigchainDB instances and update the instances respectively:

.. code:: bash

   $ kubectl --context ctx-1 apply -f configuration/config-map.yaml
   $ kubectl --context ctx-1 replace -f bigchaindb/bigchaindb-dep.yaml --force

See the page titled :ref:`How to Configure a BigchainDB Node` for more information about
ConfigMap configuration.

This will create a "rolling deployment" in Kubernetes where a new instance of
BigchainDB will be created, and if the health check on the new instance is
successful, the earlier one will be terminated. This ensures that there is
zero downtime during updates.

You can SSH to an existing BigchainDB instance and run the ``bigchaindb
show-config`` command to check that the keyring is updated.


Step 9: Deploy MongoDB Monitoring and Backup Agent
--------------------------------------------------

To Deploy MongoDB monitoring and backup agent for the new cluster, you have to authenticate each agent using its
unique client certificate. For more information on how to authenticate and add users to MongoDB please refer to:

* :ref:`Configure Users and Access Control for MongoDB<Step 13: Configure Users and Access Control for MongoDB>`

After authentication, start the Kubernetes Deployments:

* :ref:`Start a Kubernetes Deployment for MongoDB Monitoring Agent <Step 14: Start a Kubernetes Deployment for MongoDB Monitoring Agent>`.
* :ref:`Start a Kubernetes Deployment for MongoDB Backup Agent <Step 15: Start a Kubernetes Deployment for MongoDB Backup Agent>`.

.. note::
   Every MMS group has only one active Monitoring and Backup agent and having multiple agents provides High availability and failover, in case
   one goes down. For more information about Monitoring and Backup Agents please consult the `official MongoDB documenation <https://docs.cloudmanager.mongodb.com/tutorial/move-agent-to-new-server/>`_.


Step 10: Start OpenResty Service and Deployment
---------------------------------------------------------

Please refer to the following instructions:

* :ref:`Start the OpenResty Kubernetes Service <Step 8: Start the OpenResty Kubernetes Service>`.
* :ref:`Start a Kubernetes Deployment for OpenResty <Step 17: Start a Kubernetes Deployment for OpenResty>`.


Step 11: Test Your New BigchainDB Node
--------------------------------------

Please refer to the testing steps :ref:`here <Step 19: Verify the BigchainDB
Node Setup>` to verify that your new BigchainDB node is working as expected.