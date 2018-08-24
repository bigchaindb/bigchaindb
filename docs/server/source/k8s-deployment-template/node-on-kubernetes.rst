
.. Copyright BigchainDB GmbH and BigchainDB contributors
   SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
   Code is Apache-2.0 and docs are CC-BY-4.0

.. _kubernetes-template-deploy-a-single-bigchaindb-node:

Kubernetes Template: Deploy a Single BigchainDB Node
====================================================

.. note::

   A highly-available Kubernetes cluster requires at least five virtual machines
   (three for the master and two for your app's containers).
   Therefore we don't recommend using Kubernetes to run a BigchainDB node
   if that's the only thing the Kubernetes cluster will be running.
   Instead, see our :ref:`simple-deployment-template`.
   If your organization already *has* a big Kubernetes cluster running many containers,
   and your organization has people who know Kubernetes,
   then this Kubernetes deployment template might be helpful.

This page describes how to deploy a BigchainDB node
using `Kubernetes <https://kubernetes.io/>`_.
It assumes you already have a running Kubernetes cluster.

Below, we refer to many files by their directory and filename,
such as ``configuration/config-map.yaml``. Those files are files in the
`bigchaindb/bigchaindb repository on GitHub <https://github.com/bigchaindb/bigchaindb/>`_
in the ``k8s/`` directory.
Make sure you're getting those files from the appropriate Git branch on
GitHub, i.e. the branch for the version of BigchainDB that your BigchainDB
cluster is using.


Step 1: Install and Configure kubectl
-------------------------------------

kubectl is the Kubernetes CLI.
If you don't already have it installed,
then see the `Kubernetes docs to install it
<https://kubernetes.io/docs/user-guide/prereqs/>`_.

The default location of the kubectl configuration file is ``~/.kube/config``.
If you don't have that file, then you need to get it.

**Azure.** If you deployed your Kubernetes cluster on Azure
using the Azure CLI 2.0 (as per :doc:`our template
<../k8s-deployment-template/template-kubernetes-azure>`),
then you can get the ``~/.kube/config`` file using:

.. code:: bash

   $ az acs kubernetes get-credentials \
   --resource-group <name of resource group containing the cluster> \
   --name <ACS cluster name>

If it asks for a password (to unlock the SSH key)
and you enter the correct password,
but you get an error message,
then try adding ``--ssh-key-file ~/.ssh/<name>``
to the above command (i.e. the path to the private key).

.. note::

    **About kubectl contexts.** You might manage several
    Kubernetes clusters. To make it easy to switch from one to another,
    kubectl has a notion of "contexts," e.g. the context for cluster 1 or
    the context for cluster 2. To find out the current context, do:

    .. code:: bash

      $ kubectl config view

    and then look for the ``current-context`` in the output.
    The output also lists all clusters, contexts and users.
    (You might have only one of each.)
    You can switch to a different context using:

    .. code:: bash

      $ kubectl config use-context <new-context-name>

    You can also switch to a different context for just one command
    by inserting ``--context <context-name>`` into any kubectl command.
    For example:

    .. code:: bash

      $ kubectl get pods

    will get a list of the pods in the Kubernetes cluster associated
    with the context named ``k8s-bdb-test-cluster-0``.

Step 2: Connect to Your Kubernetes Cluster's Web UI (Optional)
---------------------------------------------------------------

You can connect to your cluster's
`Kubernetes Dashboard <https://kubernetes.io/docs/tasks/access-application-cluster/web-ui-dashboard/>`_
(also called the Web UI) using:

.. code:: bash

   $ kubectl proxy -p 8001

   or

   $ az acs kubernetes browse -g [Resource Group] -n [Container service instance name] --ssh-key-file /path/to/privateKey

or, if you prefer to be explicit about the context (explained above):

.. code:: bash

   $ kubectl proxy -p 8001

The output should be something like ``Starting to serve on 127.0.0.1:8001``.
That means you can visit the dashboard in your web browser at
`http://127.0.0.1:8001/ui <http://127.0.0.1:8001/ui>`_.

.. note::
    
    **Known Issue:** If you are having accessing the UI i.e.
    accessing `http://127.0.0.1:8001/ui <http://127.0.0.1:8001/ui>`_
    in your browser returns a blank page and is redirected to
    `http://127.0.0.1:8001/api/v1/namespaces/kube-system/services/kubernetes-dashboard/proxy
    <http://127.0.0.1:8001/api/v1/namespaces/kube-system/services/kubernetes-dashboard/proxy>`_
    , you can access the UI by adding a **/** at the end of the redirected URL i.e.
    `http://127.0.0.1:8001/api/v1/namespaces/kube-system/services/kubernetes-dashboard/proxy/
    <http://127.0.0.1:8001/api/v1/namespaces/kube-system/services/kubernetes-dashboard/proxy/>`_


Step 3: Configure Your BigchainDB Node
--------------------------------------

See the page titled :ref:`how-to-configure-a-bigchaindb-node`.


.. _start-the-nginx-service:

Step 4: Start the NGINX Service
-------------------------------

  * This will will give us a public IP for the cluster.

  * Once you complete this step, you might need to wait up to 10 mins for the
    public IP to be assigned.

  * You have the option to use vanilla NGINX without HTTPS support or an
    NGINX with HTTPS support.

   * Start the Kubernetes Service:

     .. code:: bash

        $ kubectl apply -f nginx-https/nginx-https-svc.yaml

        OR

        $ kubectl apply -f nginx-http/nginx-http-svc.yaml


.. _assign-dns-name-to-nginx-public-ip:

Step 5: Assign DNS Name to the NGINX Public IP
----------------------------------------------

  * This step is required only if you are planning to set up multiple
    `BigchainDB nodes
    <https://docs.bigchaindb.com/en/latest/terminology.html>`_ or are using
    HTTPS certificates tied to a domain.

  * The following command can help you find out if the NGINX service started
    above has been assigned a public IP or external IP address:

    .. code:: bash

       $ kubectl get svc -w

  * Once a public IP is assigned, you can map it to
    a DNS name.
    We usually assign ``bdb-test-node-0``, ``bdb-test-node-1`` and
    so on in our documentation.
    Let's assume that we assign the unique name of ``bdb-test-node-0`` here.


**Set up DNS mapping in Azure.**
Select the current Azure resource group and look for the ``Public IP``
resource. You should see at least 2 entries there - one for the Kubernetes
master and the other for the NGINX instance. You may have to ``Refresh`` the
Azure web page listing the resources in a resource group for the latest
changes to be reflected.
Select the ``Public IP`` resource that is attached to your service (it should
have the Azure DNS prefix name along with a long random string, without the
``master-ip`` string), select ``Configuration``, add the DNS assigned above
(for example, ``bdb-test-node-0``), click ``Save``, and wait for the
changes to be applied.

To verify the DNS setting is operational, you can run ``nslookup <DNS
name added in Azure configuration>`` from your local Linux shell.

This will ensure that when you scale to different geographical zones, other Tendermint
nodes in the network can reach this instance.


.. _start-the-mongodb-kubernetes-service:

Step 6: Start the MongoDB Kubernetes Service
--------------------------------------------

  * Start the Kubernetes Service:

    .. code:: bash

       $ kubectl apply -f mongodb/mongo-svc.yaml


.. _start-the-bigchaindb-kubernetes-service:

Step 7: Start the BigchainDB Kubernetes Service
-----------------------------------------------

  * Start the Kubernetes Service:

    .. code:: bash

       $ kubectl apply -f bigchaindb/bigchaindb-svc.yaml


.. _start-the-openresty-kubernetes-service:

Step 8(Optional): Start the OpenResty Kubernetes Service
---------------------------------------------------------

  * Start the Kubernetes Service:

    .. code:: bash

       $ kubectl apply -f nginx-openresty/nginx-openresty-svc.yaml


.. _start-the-nginx-deployment:

Step 9: Start the NGINX Kubernetes Deployment
----------------------------------------------

  * NGINX is used as a proxy to the BigchainDB, Tendermint and MongoDB instances in
    the node. It proxies HTTP/HTTPS requests on the ``node-frontend-port``
    to the corresponding OpenResty(if 3scale enabled) or BigchainDB backend, TCP connections
    on ``mongodb-frontend-port``, ``tm-p2p-port`` and ``tm-pub-key-access``
    to MongoDB and Tendermint respectively.

   * This configuration is located in the file
     ``nginx-https/nginx-https-dep.yaml`` or ``nginx-http/nginx-http-dep.yaml``.

   * Start the Kubernetes Deployment:

     .. code:: bash

        $ kubectl apply -f nginx-https/nginx-https-dep.yaml

        OR

        $ kubectl apaply -f nginx-http/nginx-http-dep.yaml


.. _create-kubernetes-storage-class-mdb:

Step 10: Create Kubernetes Storage Classes for MongoDB
------------------------------------------------------

MongoDB needs somewhere to store its data persistently,
outside the container where MongoDB is running.
Our MongoDB Docker container
(based on the official MongoDB Docker container)
exports two volume mounts with correct
permissions from inside the container:

* The directory where the MongoDB instance stores its data: ``/data/db``.
  There's more explanation in the MongoDB docs about `storage.dbpath <https://docs.mongodb.com/manual/reference/configuration-options/#storage.dbPath>`_.

* The directory where the MongoDB instance stores the metadata for a sharded
  cluster: ``/data/configdb/``.
  There's more explanation in the MongoDB docs about `sharding.configDB <https://docs.mongodb.com/manual/reference/configuration-options/#sharding.configDB>`_.

Explaining how Kubernetes handles persistent volumes,
and the associated terminology,
is beyond the scope of this documentation;
see `the Kubernetes docs about persistent volumes
<https://kubernetes.io/docs/user-guide/persistent-volumes>`_.

The first thing to do is create the Kubernetes storage classes.

**Set up Storage Classes in Azure.**
First, you need an Azure storage account.
If you deployed your Kubernetes cluster on Azure
using the Azure CLI 2.0
(as per :doc:`our template <../k8s-deployment-template/template-kubernetes-azure>`),
then the `az acs create` command already created a
storage account in the same location and resource group
as your Kubernetes cluster.
Both should have the same "storage account SKU": ``Standard_LRS``.
Standard storage is lower-cost and lower-performance.
It uses hard disk drives (HDD).
LRS means locally-redundant storage: three replicas
in the same data center.
Premium storage is higher-cost and higher-performance.
It uses solid state drives (SSD).

We recommend using Premium storage with our Kubernetes deployment template.
Create a `storage account <https://docs.microsoft.com/en-us/azure/storage/common/storage-create-storage-account>`_
for Premium storage and associate it with your Azure resource group.
For future reference, the command to create a storage account is
`az storage account create <https://docs.microsoft.com/en-us/cli/azure/storage/account#create>`_.

.. note::
    Please refer to `Azure documentation <https://docs.microsoft.com/en-us/azure/virtual-machines/windows/premium-storage>`_
    for the list of VMs that are supported by Premium Storage.

The Kubernetes template for configuration of the MongoDB Storage Class is located in the
file ``mongodb/mongo-sc.yaml``.

You may have to update the ``parameters.location`` field in the file to
specify the location you are using in Azure.

If you want to use a custom storage account with the Storage Class, you
can also update `parameters.storageAccount` and provide the Azure storage
account name.

Create the required storage classes using:

.. code:: bash

   $ kubectl apply -f mongodb/mongo-sc.yaml


You can check if it worked using ``kubectl get storageclasses``.


.. _create-kubernetes-persistent-volume-claim-mdb:

Step 11: Create Kubernetes Persistent Volume Claims for MongoDB
---------------------------------------------------------------

Next, you will create two PersistentVolumeClaim objects ``mongo-db-claim`` and
``mongo-configdb-claim``.

This configuration is located in the file ``mongodb/mongo-pvc.yaml``.

Note how there's no explicit mention of Azure, AWS or whatever.
``ReadWriteOnce`` (RWO) means the volume can be mounted as
read-write by a single Kubernetes node.
(``ReadWriteOnce`` is the *only* access mode supported
by AzureDisk.)
``storage: 20Gi`` means the volume has a size of 20
`gibibytes <https://en.wikipedia.org/wiki/Gibibyte>`_.

You may want to update the ``spec.resources.requests.storage`` field in both
the files to specify a different disk size.

Create the required Persistent Volume Claims using:

.. code:: bash

   $ kubectl apply -f mongodb/mongo-pvc.yaml


You can check its status using: ``kubectl get pvc -w``

Initially, the status of persistent volume claims might be "Pending"
but it should become "Bound" fairly quickly.

.. note::
    The default Reclaim Policy for dynamically created persistent volumes is ``Delete``
    which means the PV and its associated Azure storage resource will be automatically
    deleted on deletion of PVC or PV. In order to prevent this from happening do
    the following steps to change default reclaim policy of dyanmically created PVs
    from ``Delete`` to ``Retain``

    * Run the following command to list existing PVs

    .. Code:: bash

        $ kubectl get pv

    * Run the following command to update a PV's reclaim policy to <Retain>

    .. Code:: bash

        $ kubectl patch pv <pv-name> -p '{"spec":{"persistentVolumeReclaimPolicy":"Retain"}}'

    For notes on recreating a private volume form a released Azure disk resource consult
    :doc:`the page about cluster troubleshooting <../k8s-deployment-template/troubleshoot>`.

.. _start-kubernetes-stateful-set-mongodb:

Step 12: Start a Kubernetes StatefulSet for MongoDB
---------------------------------------------------

  * Create the MongoDB StatefulSet using:

    .. code:: bash

       $ kubectl apply -f mongodb/mongo-ss.yaml

  * It might take up to 10 minutes for the disks, specified in the Persistent
    Volume Claims above, to be created and attached to the pod.
    The UI might show that the pod has errored with the message
    "timeout expired waiting for volumes to attach/mount". Use the CLI below
    to check the status of the pod in this case, instead of the UI.
    This happens due to a bug in Azure ACS.

    .. code:: bash

       $ kubectl get pods -w


.. _configure-users-and-access-control-mongodb:

Step 13: Configure Users and Access Control for MongoDB
-------------------------------------------------------

  * In this step, you will create a user on MongoDB with authorization
    to create more users and assign roles to it. We will also create
    MongoDB client users for BigchainDB and MongoDB Monitoring agent(Optional).

    .. code:: bash

       $ kubectl apply -f mongodb/configure_mdb.sh


.. _create-kubernetes-storage-class:

Step 14: Create Kubernetes Storage Classes for BigchainDB
----------------------------------------------------------

BigchainDB needs somewhere to store Tendermint data persistently, Tendermint uses
LevelDB as the persistent storage layer.

The Kubernetes template for configuration of Storage Class is located in the
file ``bigchaindb/bigchaindb-sc.yaml``.

Details about how to create a Azure Storage account and how Kubernetes Storage Class works
are already covered in this document: :ref:`create-kubernetes-storage-class-mdb`.

Create the required storage classes using:

.. code:: bash

   $ kubectl apply -f bigchaindb/bigchaindb-sc.yaml


You can check if it worked using ``kubectl get storageclasses``.

.. _create-kubernetes-persistent-volume-claim:

Step 15: Create Kubernetes Persistent Volume Claims for BigchainDB
------------------------------------------------------------------

Next, you will create two PersistentVolumeClaim objects ``tendermint-db-claim`` and
``tendermint-config-db-claim``.

This configuration is located in the file ``bigchaindb/bigchaindb-pvc.yaml``.

Details about Kubernetes Persistent Volumes, Persistent Volume Claims
and how they work with Azure are already covered in this
document: :ref:`create-kubernetes-persistent-volume-claim-mdb`.

Create the required Persistent Volume Claims using:

.. code:: bash

   $ kubectl apply -f bigchaindb/bigchaindb-pvc.yaml

You can check its status using:

.. code::

    kubectl get pvc -w


.. _start-kubernetes-stateful-set-bdb:

Step 16: Start a Kubernetes StatefulSet for BigchainDB
------------------------------------------------------

  * This configuration is located in the file ``bigchaindb/bigchaindb-ss.yaml``.

  * Set the ``spec.serviceName`` to the value set in ``bdb-instance-name`` in
    the ConfigMap.
    For example, if the value set in the ``bdb-instance-name``
    is ``bdb-instance-0``, set the field to ``tm-instance-0``.

  * Set ``metadata.name``, ``spec.template.metadata.name`` and
    ``spec.template.metadata.labels.app`` to the value set in
    ``bdb-instance-name`` in the ConfigMap, followed by
    ``-ss``.
    For example, if the value set in the
    ``bdb-instance-name`` is ``bdb-instance-0``, set the fields to the value
    ``bdb-insance-0-ss``.

  * As we gain more experience running Tendermint in testing and production, we
    will tweak the ``resources.limits.cpu`` and ``resources.limits.memory``.

  * Create the BigchainDB StatefulSet using:

    .. code:: bash

       $ kubectl apply -f bigchaindb/bigchaindb-ss.yaml

    .. code:: bash

       $ kubectl get pods -w


.. _start-kubernetes-deployment-for-mdb-mon-agent:

Step 17(Optional): Start a Kubernetes Deployment for MongoDB Monitoring Agent
------------------------------------------------------------------------------

  * This configuration is located in the file
    ``mongodb-monitoring-agent/mongo-mon-dep.yaml``.

  * Set ``metadata.name``, ``spec.template.metadata.name`` and
    ``spec.template.metadata.labels.app`` to the value set in
    ``mdb-mon-instance-name`` in the ConfigMap, followed by
    ``-dep``.
    For example, if the value set in the
    ``mdb-mon-instance-name`` is ``mdb-mon-instance-0``, set the fields to the
    value ``mdb-mon-instance-0-dep``.

  * The configuration uses the following values set in the Secret:

    - ``mdb-mon-certs``
    - ``ca-auth``
    - ``cloud-manager-credentials``

  * Start the Kubernetes Deployment using:

    .. code:: bash

       $ kubectl apply -f mongodb-monitoring-agent/mongo-mon-dep.yaml


.. _start-kubernetes-deployment-openresty:

Step 18(Optional): Start a Kubernetes Deployment for OpenResty
--------------------------------------------------------------

  * This configuration is located in the file
    ``nginx-openresty/nginx-openresty-dep.yaml``.

  * Set ``metadata.name`` and ``spec.template.metadata.labels.app`` to the
    value set in ``openresty-instance-name`` in the ConfigMap, followed by
    ``-dep``.
    For example, if the value set in the
    ``openresty-instance-name`` is ``openresty-instance-0``, set the fields to
    the value ``openresty-instance-0-dep``.

  * Set the port to be exposed from the pod in the
    ``spec.containers[0].ports`` section. We currently expose the port at
    which OpenResty is listening for requests, ``openresty-backend-port`` in
    the above ConfigMap.

  * The configuration uses the following values set in the Secret:

    - ``threescale-credentials``

  * The configuration uses the following values set in the ConfigMap:

    - ``node-dns-server-ip``
    - ``openresty-backend-port``
    - ``ngx-bdb-instance-name``
    - ``bigchaindb-api-port``

  * Create the OpenResty Deployment using:

    .. code:: bash

       $ kubectl apply -f nginx-openresty/nginx-openresty-dep.yaml


  * You can check its status using the command ``kubectl get deployments -w``


Step 19(Optional): Configure the MongoDB Cloud Manager
------------------------------------------------------

Refer to the
:doc:`documentation <../k8s-deployment-template/cloud-manager>`
for details on how to configure the MongoDB Cloud Manager to enable
monitoring and backup.


Step 20(Optional): Only for multi site deployments(Geographically dispersed)
----------------------------------------------------------------------------

We need to make sure that clusters are able
to talk to each other i.e. specifically the communication between the
Tendermint peers. Set up networking between the clusters using
`Kubernetes Services <https://kubernetes.io/docs/concepts/services-networking/service/>`_.

Assuming we have a BigchainDB instance ``bdb-instance-1`` residing in Azure data center location ``westeurope`` and we
want to connect to ``bdb-instance-2``, ``bdb-instance-3``, and ``bdb-instance-4`` located in Azure data centers
``eastus``, ``centralus`` and ``westus``, respectively. Unless you already have explicitly set up networking for
``bdb-instance-1`` to communicate with ``bdb-instance-2/3/4`` and
vice versa, we will have to add a Kubernetes Service in each cluster to accomplish this goal in order to set up a
Tendermint P2P network.
It is similar to ensuring that there is a ``CNAME`` record in the DNS
infrastructure to resolve ``bdb-instance-X`` to the host where it is actually available.
We can do this in Kubernetes using a Kubernetes Service of ``type``
``ExternalName``.

* This configuration is located in the file ``bigchaindb/bigchaindb-ext-conn-svc.yaml``.

* Set the name of the ``metadata.name`` to the host name of the BigchainDB instance you are trying to connect to.
  For instance if you are configuring this service on cluster with ``bdb-instance-1`` then the ``metadata.name`` will
  be ``bdb-instance-2`` and vice versa.

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
   share with them your instance name (``tendermint-instance-name`` in the ConfigMap)
   and the FQDN of the NGINX instance acting as Gateway(set in: :ref:`Assign DNS name to NGINX
   Public IP <assign-dns-name-to-nginx-public-ip>`).


.. _verify-and-test-bdb:

Step 21: Verify the BigchainDB Node Setup
-----------------------------------------

Step 21.1: Testing Internally
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To test the setup of your BigchainDB node, you could use a Docker container
that provides utilities like ``nslookup``, ``curl`` and ``dig``.
For example, you could use a container based on our
`bigchaindb/toolbox <https://hub.docker.com/r/bigchaindb/toolbox/>`_ image.
(The corresponding
`Dockerfile <https://github.com/bigchaindb/bigchaindb/blob/master/k8s/toolbox/Dockerfile>`_
is in the ``bigchaindb/bigchaindb`` repository on GitHub.)
You can use it as below to get started immediately:

.. code:: bash

   $ kubectl   \
      run -it toolbox \
      --image bigchaindb/toolbox \
      --image-pull-policy=Always \
      --restart=Never --rm

It will drop you to the shell prompt.

To test the MongoDB instance:

.. code:: bash

   $ nslookup mdb-instance-0

   $ dig +noall +answer _mdb-port._tcp.mdb-instance-0.default.svc.cluster.local SRV

   $ curl -X GET http://mdb-instance-0:27017

The ``nslookup`` command should output the configured IP address of the service
(in the cluster).
The ``dig`` command should return the configured port numbers.
The ``curl`` command tests the availability of the service.

To test the BigchainDB instance:

.. code:: bash

   $ nslookup bdb-instance-0

   $ dig +noall +answer _bdb-api-port._tcp.bdb-instance-0.default.svc.cluster.local SRV

   $ dig +noall +answer _bdb-ws-port._tcp.bdb-instance-0.default.svc.cluster.local SRV

   $ curl -X GET http://bdb-instance-0:9984

   $ curl -X GET http://bdb-instance-0:9986/pub_key.json

   $ curl -X GET http://bdb-instance-0:26657/abci_info

   $ wsc -er ws://bdb-instance-0:9985/api/v1/streams/valid_transactions


To test the OpenResty instance:

.. code:: bash

   $ nslookup openresty-instance-0

   $ dig +noall +answer _openresty-svc-port._tcp.openresty-instance-0.default.svc.cluster.local SRV

To verify if OpenResty instance forwards the requests properly, send a ``POST``
transaction to OpenResty at post ``80`` and check the response from the backend
BigchainDB instance.


To test the vanilla NGINX instance:

.. code:: bash

   $ nslookup ngx-http-instance-0

   $ dig +noall +answer _public-node-port._tcp.ngx-http-instance-0.default.svc.cluster.local SRV

   $ dig +noall +answer _public-health-check-port._tcp.ngx-http-instance-0.default.svc.cluster.local SRV

   $ wsc -er ws://ngx-http-instance-0/api/v1/streams/valid_transactions

   $ curl -X GET http://ngx-http-instance-0:27017

The above curl command should result in the response
``It looks like you are trying to access MongoDB over HTTP on the native driver port.``



To test the NGINX instance with HTTPS and 3scale integration:

.. code:: bash

   $ nslookup ngx-instance-0

   $ dig +noall +answer _public-secure-node-port._tcp.ngx-instance-0.default.svc.cluster.local SRV

   $ dig +noall +answer _public-mdb-port._tcp.ngx-instance-0.default.svc.cluster.local SRV

   $ dig +noall +answer _public-insecure-node-port._tcp.ngx-instance-0.default.svc.cluster.local SRV

   $ wsc -er wss://<node-fqdn>/api/v1/streams/valid_transactions

   $ curl -X GET http://<node-fqdn>:27017

The above curl command should result in the response
``It looks like you are trying to access MongoDB over HTTP on the native driver port.``


Step 21.2: Testing Externally
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Check the MongoDB monitoring agent on the MongoDB Cloud Manager
portal to verify they are working fine.

If you are using the NGINX with HTTP support, accessing the URL
``http://<DNS/IP of your exposed BigchainDB service endpoint>:node-frontend-port``
on your browser should result in a JSON response that shows the BigchainDB
server version, among other things.
If you are using the NGINX with HTTPS support, use ``https`` instead of
``http`` above.

Use the Python Driver to send some transactions to the BigchainDB node and
verify that your node or cluster works as expected.

Next, you can set up log analytics and monitoring, by following our templates:

* :doc:`../k8s-deployment-template/log-analytics`.
