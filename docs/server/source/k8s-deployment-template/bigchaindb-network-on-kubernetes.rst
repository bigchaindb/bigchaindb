
.. Copyright BigchainDB GmbH and BigchainDB contributors
   SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
   Code is Apache-2.0 and docs are CC-BY-4.0

.. _kubernetes-template-deploy-bigchaindb-network:

Kubernetes Template: Deploying a BigchainDB network
===================================================

.. note::

   A highly-available Kubernetes cluster requires at least five virtual machines
   (three for the master and two for your app's containers).
   Therefore we don't recommend using Kubernetes to run a BigchainDB node
   if that's the only thing the Kubernetes cluster will be running.
   Instead, see our :ref:`simple-deployment-template`.
   If your organization already *has* a big Kubernetes cluster running many containers,
   and your organization has people who know Kubernetes,
   then this Kubernetes deployment template might be helpful.

This page describes how to deploy a static BigchainDB + Tendermint network.

If you want to deploy a stand-alone BigchainDB node in a BigchainDB cluster,
or a stand-alone BigchainDB node,
then see :doc:`the page about that <node-on-kubernetes>`.

We can use this guide to deploy a BigchainDB network in the following scenarios:

*  Single Azure Kubernetes Site.
*  Multiple Azure Kubernetes Sites (Geographically dispersed).


Terminology Used
----------------

``BigchainDB node`` is a set of Kubernetes components that join together to
form a BigchainDB single node. Please refer to the :doc:`architecture diagram <architecture>`
for more details.

``BigchainDB network`` will refer to a collection of nodes working together
to form a network.


Below, we refer to multiple files by their directory and filename,
such as ``bigchaindb/bigchaindb-ext-conn-svc.yaml``. Those files are located in the
`bigchaindb/bigchaindb repository on GitHub
<https://github.com/bigchaindb/bigchaindb/>`_ in the ``k8s/`` directory.
Make sure you're getting those files from the appropriate Git branch on
GitHub, i.e. the branch for the version of BigchainDB that your BigchainDB
cluster is using.

.. note::

   This deployment strategy is currently used for testing purposes only,
   operated by a single stakeholder or tightly coupled stakeholders.

.. note::

  Currently, we only support a static set of participants in the network.
  Once a BigchainDB network is started with a certain number of validators
  and a genesis file. Users cannot add new validator nodes dynamically.
  You can track the progress of this funtionality on our
  `github repository <https://github.com/bigchaindb/bigchaindb/milestones>`_.


.. _pre-reqs-bdb-network:

Prerequisites
-------------

The deployment methodology is similar to one covered with :doc:`node-on-kubernetes`, but
we need to tweak some configurations depending on your choice of deployment.

The operator needs to follow some consistent naming convention for all the components
covered :ref:`here <things-each-node-operator-must-do>`.

Lets assume we are deploying a 4 node cluster, your naming conventions could look like this:

.. code::

  {
    "MongoDB": [
      "mdb-instance-1",
      "mdb-instance-2",
      "mdb-instance-3",
      "mdb-instance-4"
    ],
    "BigchainDB": [
      "bdb-instance-1",
      "bdb-instance-2",
      "bdb-instance-3",
      "bdb-instance-4"
    ],
    "NGINX": [
      "ngx-instance-1",
      "ngx-instance-2",
      "ngx-instance-3",
      "ngx-instance-4"
    ],
    "OpenResty": [
      "openresty-instance-1",
      "openresty-instance-2",
      "openresty-instance-3",
      "openresty-instance-4"
    ],
    "MongoDB_Monitoring_Agent": [
      "mdb-mon-instance-1",
      "mdb-mon-instance-2",
      "mdb-mon-instance-3",
      "mdb-mon-instance-4"
    ]
  }

.. note::

  Blockchain Genesis ID and Time will be shared across all nodes.

Edit config.yaml and secret.yaml
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Make N(number of nodes) copies of ``configuration/config-map.yaml`` and ``configuration/secret.yaml``.

.. code:: text

  # For config-map.yaml
  config-map-node-1.yaml
  config-map-node-2.yaml
  config-map-node-3.yaml
  config-map-node-4.yaml

  # For secret.yaml
  secret-node-1.yaml
  secret-node-2.yaml
  secret-node-3.yaml
  secret-node-4.yaml

Edit the data values as described in :doc:`this document <node-config-map-and-secrets>`, based
on the naming convention described :ref:`above <pre-reqs-bdb-network>`.

**Only for single site deployments**: Since all the configuration files use the
same ConfigMap and Secret Keys i.e.
``metadata.name -> vars, bdb-config and tendermint-config`` and
``metadata.name -> cloud-manager-credentials, mdb-certs, mdb-mon-certs, bdb-certs,``
``https-certs, three-scale-credentials, ca-auth`` respectively, each file
will overwrite the configuration of the previously deployed one.
We want each node to have its own unique configurations.
One way to go about it is that, using the
:ref:`naming convention above <pre-reqs-bdb-network>` we edit the ConfigMap and Secret keys.

.. code:: text

  # For config-map-node-1.yaml
  metadata.name: vars -> vars-node-1
  metadata.name: bdb-config -> bdb-config-node-1
  metadata.name: tendermint-config -> tendermint-config-node-1

  # For secret-node-1.yaml
  metadata.name: cloud-manager-credentials -> cloud-manager-credentials-node-1
  metadata.name: mdb-certs -> mdb-certs-node-1
  metadata.name: mdb-mon-certs -> mdb-mon-certs-node-1
  metadata.name: bdb-certs -> bdb-certs-node-1
  metadata.name: https-certs -> https-certs-node-1
  metadata.name: threescale-credentials -> threescale-credentials-node-1
  metadata.name: ca-auth -> ca-auth-node-1

  # Repeat for the remaining files.

Deploy all your configuration maps and secrets.

.. code:: bash

  kubectl apply -f configuration/config-map-node-1.yaml
  kubectl apply -f configuration/config-map-node-2.yaml
  kubectl apply -f configuration/config-map-node-3.yaml
  kubectl apply -f configuration/config-map-node-4.yaml
  kubectl apply -f configuration/secret-node-1.yaml
  kubectl apply -f configuration/secret-node-2.yaml
  kubectl apply -f configuration/secret-node-3.yaml
  kubectl apply -f configuration/secret-node-4.yaml

.. note::

  Similar to what we did, with config-map.yaml and secret.yaml i.e. indexing them
  per node, we have to do the same for each Kubernetes component
  i.e. Services, StorageClasses, PersistentVolumeClaims, StatefulSets, Deployments etc.

.. code:: text

  # For Services
  *-node-1-svc.yaml
  *-node-2-svc.yaml
  *-node-3-svc.yaml
  *-node-4-svc.yaml

  # For StorageClasses
  *-node-1-sc.yaml
  *-node-2-sc.yaml
  *-node-3-sc.yaml
  *-node-4-sc.yaml

  # For PersistentVolumeClaims
  *-node-1-pvc.yaml
  *-node-2-pvc.yaml
  *-node-3-pvc.yaml
  *-node-4-pvc.yaml

  # For StatefulSets
  *-node-1-ss.yaml
  *-node-2-ss.yaml
  *-node-3-ss.yaml
  *-node-4-ss.yaml

  # For Deployments
  *-node-1-dep.yaml
  *-node-2-dep.yaml
  *-node-3-dep.yaml
  *-node-4-dep.yaml


.. _single-site-network:

Single Site: Single Azure Kubernetes Cluster
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For the deployment of a BigchainDB network under a single cluster, we need to replicate
the :doc:`deployment steps for each node <node-on-kubernetes>` N number of times, N being
the number of participants in the network.

In our Kubernetes deployment template for a single BigchainDB node, we covered the basic configurations
settings :ref:`here <how-to-configure-a-bigchaindb-node>`.

Since, we index the ConfigMap and Secret Keys for the single site deployment, we need to update
all the Kubernetes components to reflect the corresponding changes i.e. For each Kubernetes Service,
StatefulSet, PersistentVolumeClaim, Deployment, and StorageClass, we need to update the respective
`*.yaml` file and update the ConfigMapKeyRef.name OR secret.secretName.

Example
"""""""

Assuming we are deploying the MongoDB StatefulSet for Node 1. We need to update
the ``mongo-node-1-ss.yaml`` and update the corresponding ConfigMapKeyRef.name or secret.secretNames.

.. code:: text

  ########################################################################
  # This YAML file desribes a StatefulSet with a service for running and #
  # exposing a MongoDB instance.                                         #
  # It depends on the configdb and db k8s pvc.                           #
  ########################################################################

  apiVersion: apps/v1beta1
  kind: StatefulSet
  metadata:
    name: mdb-instance-0-ss
    namespace: default
  spec:
    serviceName: mdb-instance-0
    replicas: 1
    template:
      metadata:
        name: mdb-instance-0-ss
        labels:
          app: mdb-instance-0-ss
      spec:
        terminationGracePeriodSeconds: 10
        containers:
        - name: mongodb
          image: bigchaindb/mongodb:3.2
          imagePullPolicy: IfNotPresent
          env:
          - name: MONGODB_FQDN
            valueFrom:
              configMapKeyRef:
               name: vars-1 # Changed from ``vars``
               key: mdb-instance-name
          - name: MONGODB_POD_IP
            valueFrom:
              fieldRef:
                fieldPath: status.podIP
          - name: MONGODB_PORT
            valueFrom:
              configMapKeyRef:
               name: vars-1 # Changed from ``vars``
               key: mongodb-backend-port
          - name: STORAGE_ENGINE_CACHE_SIZE
            valueFrom:
              configMapKeyRef:
               name: vars-1 # Changed from ``vars``
               key: storage-engine-cache-size
          args:
          - --mongodb-port
          - $(MONGODB_PORT)
          - --mongodb-key-file-path
          - /etc/mongod/ssl/mdb-instance.pem
          - --mongodb-ca-file-path
          - /etc/mongod/ca/ca.pem
          - --mongodb-crl-file-path
          - /etc/mongod/ca/crl.pem
          - --mongodb-fqdn
          - $(MONGODB_FQDN)
          - --mongodb-ip
          - $(MONGODB_POD_IP)
          - --storage-engine-cache-size
          - $(STORAGE_ENGINE_CACHE_SIZE)
          securityContext:
            capabilities:
              add:
              - FOWNER
          ports:
          - containerPort: "<mongodb-backend-port from ConfigMap>"
            protocol: TCP
            name: mdb-api-port
          volumeMounts:
          - name: mdb-db
            mountPath: /data/db
          - name: mdb-configdb
            mountPath: /data/configdb
          - name: mdb-certs
            mountPath: /etc/mongod/ssl/
            readOnly: true
          - name: ca-auth
            mountPath: /etc/mongod/ca/
            readOnly: true
          resources:
            limits:
              cpu: 200m
              memory: 5G
          livenessProbe:
            tcpSocket:
              port: mdb-api-port
            initialDelaySeconds: 15
            successThreshold: 1
            failureThreshold: 3
            periodSeconds: 15
            timeoutSeconds: 10
        restartPolicy: Always
        volumes:
        - name: mdb-db
          persistentVolumeClaim:
            claimName: mongo-db-claim-1 # Changed from ``mongo-db-claim``
        - name: mdb-configdb
          persistentVolumeClaim:
            claimName: mongo-configdb-claim-1 # Changed from ``mongo-configdb-claim``
        - name: mdb-certs
          secret:
            secretName: mdb-certs-1 # Changed from ``mdb-certs``
            defaultMode: 0400
        - name: ca-auth
          secret:
            secretName: ca-auth-1 # Changed from ``ca-auth``
            defaultMode: 0400

The above example is meant to be repeated for all the Kubernetes components of a BigchainDB node.

* ``nginx-http/nginx-http-node-X-svc.yaml`` or ``nginx-https/nginx-https-node-X-svc.yaml``

* ``nginx-http/nginx-http-node-X-dep.yaml`` or ``nginx-https/nginx-https-node-X-dep.yaml``

* ``mongodb/mongodb-node-X-svc.yaml``

* ``mongodb/mongodb-node-X-sc.yaml``

* ``mongodb/mongodb-node-X-pvc.yaml``

* ``mongodb/mongodb-node-X-ss.yaml``

* ``bigchaindb/bigchaindb-node-X-svc.yaml``

* ``bigchaindb/bigchaindb-node-X-sc.yaml``

* ``bigchaindb/bigchaindb-node-X-pvc.yaml``

* ``bigchaindb/bigchaindb-node-X-ss.yaml``

* ``nginx-openresty/nginx-openresty-node-X-svc.yaml``

* ``nginx-openresty/nginx-openresty-node-X-dep.yaml``


Multi Site: Multiple Azure Kubernetes Clusters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For the multi site deployment of a BigchainDB network with geographically dispersed
nodes, we need to replicate the :doc:`deployment steps for each node <node-on-kubernetes>` N number of times,
N being the number of participants in the network.

The operator needs to follow a consistent naming convention which has :ref:`already
discussed in this document <pre-reqs-bdb-network>`.

.. note::

  Assuming we are using independent Kubernetes clusters, the ConfigMap and Secret Keys
  do not need to be updated unlike :ref:`single-site-network`, and we also do not
  need to update corresponding ConfigMap/Secret imports in the Kubernetes components.


Deploy Kubernetes Services
--------------------------

Deploy the following services for each node by following the naming convention
described :ref:`above <pre-reqs-bdb-network>`:

* :ref:`Start the NGINX Service <start-the-nginx-service>`.

* :ref:`Assign DNS Name to the NGINX Public IP <assign-dns-name-to-nginx-public-ip>`

* :ref:`Start the MongoDB Kubernetes Service <start-the-mongodb-kubernetes-service>`.

* :ref:`Start the BigchainDB Kubernetes Service <start-the-bigchaindb-kubernetes-service>`.

* :ref:`Start the OpenResty Kubernetes Service <start-the-openresty-kubernetes-service>`.


Only for multi site deployments
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We need to make sure that clusters are able
to talk to each other i.e. specifically the communication between the
BigchainDB peers. Set up networking between the clusters using
`Kubernetes Services <https://kubernetes.io/docs/concepts/services-networking/service/>`_.

Assuming we have a BigchainDB instance ``bigchaindb-instance-1`` residing in Azure data center location ``westeurope`` and we
want to connect to ``bigchaindb-instance-2``, ``bigchaindb-instance-3``, and ``bigchaindb-instance-4`` located in Azure data centers
``eastus``, ``centralus`` and ``westus``, respectively. Unless you already have explicitly set up networking for
``bigchaindb-instance-1`` to communicate with ``bigchaindb-instance-2/3/4`` and
vice versa, we will have to add a Kubernetes Service in each cluster to accomplish this goal in order to set up a
BigchainDB P2P network.
It is similar to ensuring that there is a ``CNAME`` record in the DNS
infrastructure to resolve ``bigchaindb-instance-X`` to the host where it is actually available.
We can do this in Kubernetes using a Kubernetes Service of ``type``
``ExternalName``.

* This configuration is located in the file ``bigchaindb/bigchaindb-ext-conn-svc.yaml``.

* Set the name of the ``metadata.name`` to the host name of the BigchainDB instance you are trying to connect to.
  For instance if you are configuring this service on cluster with ``bigchaindb-instance-1`` then the ``metadata.name`` will
  be ``bigchaindb-instance-2`` and vice versa.

* Set ``spec.ports.port[0]`` to the ``tm-p2p-port`` from the ConfigMap for the other cluster.

* Set ``spec.ports.port[1]`` to the ``tm-rpc-port`` from the ConfigMap for the other cluster.

* Set ``spec.externalName`` to the FQDN mapped to NGINX Public IP of the cluster you are trying to connect to.
  For more information about the FQDN please refer to: :ref:`Assign DNS name to NGINX Public
  IP <assign-dns-name-to-nginx-public-ip>`.

.. note::
   This operation needs to be replicated ``n-1`` times per node for a ``n`` node cluster, with the respective FQDNs
   we need to communicate with.

   If you are not the system administrator of the cluster, you have to get in
   touch with the system administrator/s of the other ``n-1`` clusters and
   share with them your instance name (``bigchaindb-instance-name`` in the ConfigMap)
   and the FQDN of the NGINX instance acting as Gateway(set in: :ref:`Assign DNS name to NGINX
   Public IP <assign-dns-name-to-nginx-public-ip>`).


Start NGINX Kubernetes deployments
----------------------------------

Start the NGINX deployment that serves as a Gateway for each node by following the
naming convention described :ref:`above <pre-reqs-bdb-network>` and referring to the following instructions:

* :ref:`Start the NGINX Kubernetes Deployment <start-the-nginx-deployment>`.


Deploy Kubernetes StorageClasses for MongoDB and BigchainDB
------------------------------------------------------------

Deploy the following StorageClasses for each node by following the naming convention
described :ref:`above <pre-reqs-bdb-network>`:

* :ref:`Create Kubernetes Storage Classes for MongoDB <create-kubernetes-storage-class-mdb>`.

* :ref:`Create Kubernetes Storage Classes for BigchainDB <create-kubernetes-storage-class>`.


Deploy Kubernetes PersistentVolumeClaims for MongoDB and BigchainDB
--------------------------------------------------------------------

Deploy the following services for each node by following the naming convention
described :ref:`above <pre-reqs-bdb-network>`:

* :ref:`Create Kubernetes Persistent Volume Claims for MongoDB <create-kubernetes-persistent-volume-claim-mdb>`.

* :ref:`Create Kubernetes Persistent Volume Claims for BigchainDB <create-kubernetes-persistent-volume-claim>`


Deploy MongoDB Kubernetes StatefulSet
--------------------------------------

Deploy the MongoDB StatefulSet (standalone MongoDB) for each node by following the naming convention
described :ref:`above <pre-reqs-bdb-network>`: and referring to the following section:

* :ref:`Start a Kubernetes StatefulSet for MongoDB <start-kubernetes-stateful-set-mongodb>`.


Configure Users and Access Control for MongoDB
----------------------------------------------

Configure users and access control for each MongoDB instance
in the network by referring to the following section:

* :ref:`Configure Users and Access Control for MongoDB <configure-users-and-access-control-mongodb>`.


Start Kubernetes StatefulSet for BigchainDB
-------------------------------------------

Start the BigchainDB Kubernetes StatefulSet for each node by following the
naming convention described :ref:`above <pre-reqs-bdb-network>` and referring to the following instructions:

* :ref:`Start a Kubernetes Deployment for BigchainDB <start-kubernetes-stateful-set-bdb>`.


Start Kubernetes Deployment for MongoDB Monitoring Agent
---------------------------------------------------------

Start the MongoDB monitoring agent Kubernetes deployment for each node by following the
naming convention described :ref:`above <pre-reqs-bdb-network>` and referring to the following instructions:

* :ref:`Start a Kubernetes Deployment for MongoDB Monitoring Agent <start-kubernetes-deployment-for-mdb-mon-agent>`.


Start Kubernetes Deployment for OpenResty
------------------------------------------

Start the OpenResty Kubernetes deployment for each node by following the
naming convention described :ref:`above <pre-reqs-bdb-network>` and referring to the following instructions:

* :ref:`Start a Kubernetes Deployment for OpenResty <start-kubernetes-deployment-openresty>`.


Verify and Test
---------------

Verify and test your setup by referring to the following instructions:

* :ref:`Verify the BigchainDB Node Setup <verify-and-test-bdb>`.

