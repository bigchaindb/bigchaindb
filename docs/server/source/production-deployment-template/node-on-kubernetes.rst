Kubernetes Template: Deploy a Single BigchainDB Node
====================================================

This page describes how to deploy the first BigchainDB node
in a BigchainDB cluster, or a stand-alone BigchainDB node,
using `Kubernetes <https://kubernetes.io/>`_.
It assumes you already have a running Kubernetes cluster.

If you want to add a new BigchainDB node to an existing BigchainDB cluster,
refer to :doc:`the page about that <add-node-on-kubernetes>`.

Below, we refer to many files by their directory and filename,
such as ``configuration/config-map.yaml``. Those files are files in the
`bigchaindb/bigchaindb repository on GitHub
<https://github.com/bigchaindb/bigchaindb/>`_ in the ``k8s/`` directory.
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
using the Azure CLI 2.0 (as per :doc:`our template <template-kubernetes-azure>`),
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

      $ kubectl --context k8s-bdb-test-cluster-0 get pods

    will get a list of the pods in the Kubernetes cluster associated
    with the context named ``k8s-bdb-test-cluster-0``.

Step 2: Connect to Your Cluster's Web UI (Optional)
---------------------------------------------------

You can connect to your cluster's
`Kubernetes Dashboard <https://kubernetes.io/docs/tasks/access-application-cluster/web-ui-dashboard/>`_
(also called the Web UI) using:

.. code:: bash

   $ kubectl proxy -p 8001

or, if you prefer to be explicit about the context (explained above):

.. code:: bash

   $ kubectl --context k8s-bdb-test-cluster-0 proxy -p 8001

The output should be something like ``Starting to serve on 127.0.0.1:8001``.
That means you can visit the dashboard in your web browser at
`http://127.0.0.1:8001/ui <http://127.0.0.1:8001/ui>`_.


Step 3: Configure Your BigchainDB Node
--------------------------------------

See the page titled :ref:`How to Configure a BigchainDB Node`.
   

Step 4: Start the NGINX Service
-------------------------------

  * This will will give us a public IP for the cluster.

  * Once you complete this step, you might need to wait up to 10 mins for the
    public IP to be assigned.

  * You have the option to use vanilla NGINX without HTTPS support or an
    OpenResty NGINX integrated with 3scale API Gateway.


Step 4.1: Vanilla NGINX
^^^^^^^^^^^^^^^^^^^^^^^

   * This configuration is located in the file ``nginx/nginx-svc.yaml``.
    
   * Set the ``metadata.name`` and ``metadata.labels.name`` to the value
     set in ``ngx-instance-name`` in the ConfigMap above.
   
   * Set the ``spec.selector.app`` to the value set in ``ngx-instance-name`` in
     the ConfigMap followed by ``-dep``. For example, if the value set in the
     ``ngx-instance-name`` is ``ngx-instance-0``, set  the
     ``spec.selector.app`` to ``ngx-instance-0-dep``.
   
   * Start the Kubernetes Service:

     .. code:: bash
     
        $ kubectl --context k8s-bdb-test-cluster-0 apply -f nginx/nginx-svc.yaml


Step 4.2: OpenResty NGINX + 3scale
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

   * You have to enable HTTPS for this one and will need an HTTPS certificate
     for your domain.
      
   * You should have already created the necessary Kubernetes Secrets in the previous
     step (e.g. ``https-certs`` and ``threescale-credentials``).

   * This configuration is located in the file ``nginx-3scale/nginx-3scale-svc.yaml``.

   * Set the ``metadata.name`` and ``metadata.labels.name`` to the value
     set in ``ngx-instance-name`` in the ConfigMap above.

   * Set the ``spec.selector.app`` to the value set in ``ngx-instance-name`` in
     the ConfigMap followed by ``-dep``. For example, if the value set in the
     ``ngx-instance-name`` is ``ngx-instance-0``, set  the
     ``spec.selector.app`` to ``ngx-instance-0-dep``.
   
   * Start the Kubernetes Service:
   
     .. code:: bash

        $ kubectl --context k8s-bdb-test-cluster-0 apply -f nginx-3scale/nginx-3scale-svc.yaml


Step 5: Assign DNS Name to the NGINX Public IP
----------------------------------------------

  * This step is required only if you are planning to set up multiple
    `BigchainDB nodes
    <https://docs.bigchaindb.com/en/latest/terminology.html>`_ or are using
    HTTPS certificates tied to a domain.

  * The following command can help you find out if the NGINX service started
    above has been assigned a public IP or external IP address:
   
    .. code:: bash

       $ kubectl --context k8s-bdb-test-cluster-0 get svc -w
   
  * Once a public IP is assigned, you can map it to
    a DNS name.
    We usually assign ``bdb-test-cluster-0``, ``bdb-test-cluster-1`` and
    so on in our documentation.
    Let's assume that we assign the unique name of ``bdb-test-cluster-0`` here.


**Set up DNS mapping in Azure.**
Select the current Azure resource group and look for the ``Public IP``
resource. You should see at least 2 entries there - one for the Kubernetes
master and the other for the MongoDB instance. You may have to ``Refresh`` the
Azure web page listing the resources in a resource group for the latest
changes to be reflected.
Select the ``Public IP`` resource that is attached to your service (it should
have the Azure DNS prefix name along with a long random string, without the
``master-ip`` string), select ``Configuration``, add the DNS assigned above
(for example, ``bdb-test-cluster-0``), click ``Save``, and wait for the
changes to be applied.

To verify the DNS setting is operational, you can run ``nslookup <DNS
name added in ConfigMap>`` from your local Linux shell.

This will ensure that when you scale the replica set later, other MongoDB
members in the replica set can reach this instance.


Step 6: Start the MongoDB Kubernetes Service
--------------------------------------------

  * This configuration is located in the file ``mongodb/mongo-svc.yaml``.

  * Set the ``metadata.name`` and ``metadata.labels.name`` to the value
    set in ``mdb-instance-name`` in the ConfigMap above.
  
  * Set the ``spec.selector.app`` to the value set in ``mdb-instance-name`` in
    the ConfigMap followed by ``-ss``. For example, if the value set in the
    ``mdb-instance-name`` is ``mdb-instance-0``, set  the
    ``spec.selector.app`` to ``mdb-instance-0-ss``.
  
  * Start the Kubernetes Service:

    .. code:: bash

       $ kubectl --context k8s-bdb-test-cluster-0 apply -f mongodb/mongo-svc.yaml


Step 7: Start the BigchainDB Kubernetes Service
-----------------------------------------------

  * This configuration is located in the file ``bigchaindb/bigchaindb-svc.yaml``.

  * Set the ``metadata.name`` and ``metadata.labels.name`` to the value
    set in ``bdb-instance-name`` in the ConfigMap above.
  
  * Set the ``spec.selector.app`` to the value set in ``bdb-instance-name`` in
    the ConfigMap followed by ``-dep``. For example, if the value set in the
    ``bdb-instance-name`` is ``bdb-instance-0``, set  the
    ``spec.selector.app`` to ``bdb-instance-0-dep``.

  * Start the Kubernetes Service:

    .. code:: bash

       $ kubectl --context k8s-bdb-test-cluster-0 apply -f bigchaindb/bigchaindb-svc.yaml


Step 8: Start the NGINX Kubernetes Deployment
---------------------------------------------

  * NGINX is used as a proxy to both the BigchainDB and MongoDB instances in
    the node. It proxies HTTP requests on port 80 to the BigchainDB backend,
    and TCP connections on port 27017 to the MongoDB backend.

  * As in step 4, you have the option to use vanilla NGINX or an OpenResty
    NGINX integrated with 3scale API Gateway.

Step 8.1: Vanilla NGINX
^^^^^^^^^^^^^^^^^^^^^^^
  
  * This configuration is located in the file ``nginx/nginx-dep.yaml``.
    
  * Set the ``metadata.name`` and ``spec.template.metadata.labels.app``
    to the value set in ``ngx-instance-name`` in the ConfigMap followed by a
    ``-dep``. For example, if the value set in the ``ngx-instance-name`` is
    ``ngx-instance-0``, set the fields to ``ngx-instance-0-dep``.

  * Set ``MONGODB_BACKEND_HOST`` env var to
    the value set in ``mdb-instance-name`` in the ConfigMap, followed by
    ``.default.svc.cluster.local``. For example, if the value set in the
    ``mdb-instance-name`` is ``mdb-instance-0``, set the
    ``MONGODB_BACKEND_HOST`` env var to
    ``mdb-instance-0.default.svc.cluster.local``.
    
  * Set ``BIGCHAINDB_BACKEND_HOST`` env var to
    the value set in ``bdb-instance-name`` in the ConfigMap, followed by
    ``.default.svc.cluster.local``. For example, if the value set in the
    ``bdb-instance-name`` is ``bdb-instance-0``, set the
    ``BIGCHAINDB_BACKEND_HOST`` env var to
    ``bdb-instance-0.default.svc.cluster.local``.
    
  * Set ``MONGODB_FRONTEND_PORT`` to 27017, or the port number on which you
    want to expose MongoDB service.
    
  * Set ``BIGCHAINDB_FRONTEND_PORT`` to 80, or the port number on which you
    want to expose BigchainDB service.
    
  * Start the Kubernetes Deployment:

    .. code:: bash

       $ kubectl --context k8s-bdb-test-cluster-0 apply -f nginx/nginx-dep.yaml


Step 8.2: OpenResty NGINX + 3scale
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   
   * This configuration is located in the file
     ``nginx-3scale/nginx-3scale-dep.yaml``.

   * Set the ``metadata.name`` and ``spec.template.metadata.labels.app``
     to the value set in ``ngx-instance-name`` in the ConfigMap followed by a
     ``-dep``. For example, if the value set in the ``ngx-instance-name`` is
     ``ngx-instance-0``, set the fields to ``ngx-instance-0-dep``.

   * Set ``MONGODB_BACKEND_HOST`` env var to
     the value set in ``mdb-instance-name`` in the ConfigMap, followed by
     ``.default.svc.cluster.local``. For example, if the value set in the
     ``mdb-instance-name`` is ``mdb-instance-0``, set the
     ``MONGODB_BACKEND_HOST`` env var to
     ``mdb-instance-0.default.svc.cluster.local``.
     
   * Set ``BIGCHAINDB_BACKEND_HOST`` env var to
     the value set in ``bdb-instance-name`` in the ConfigMap, followed by
     ``.default.svc.cluster.local``. For example, if the value set in the
     ``bdb-instance-name`` is ``bdb-instance-0``, set the
     ``BIGCHAINDB_BACKEND_HOST`` env var to
     ``bdb-instance-0.default.svc.cluster.local``.
     
   * Set ``MONGODB_FRONTEND_PORT`` to 27017, or the port number on which you
     want to expose the MongoDB service.
     
   * Set ``BIGCHAINDB_FRONTEND_PORT`` to 443, or the port number on which you
     want to expose the BigchainDB service over HTTPS.

   * Start the Kubernetes Deployment:

     .. code:: bash

        $ kubectl --context k8s-bdb-test-cluster-0 apply -f nginx-3scale/nginx-3scale-dep.yaml


Step 9: Create Kubernetes Storage Classes for MongoDB
-----------------------------------------------------

MongoDB needs somewhere to store its data persistently,
outside the container where MongoDB is running.
Our MongoDB Docker container
(based on the official MongoDB Docker container)
exports two volume mounts with correct
permissions from inside the container:

* The directory where the mongod instance stores its data: ``/data/db``.
  There's more explanation in the MongoDB docs about `storage.dbpath <https://docs.mongodb.com/manual/reference/configuration-options/#storage.dbPath>`_.

* The directory where the mongodb instance stores the metadata for a sharded
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
(as per :doc:`our template <template-kubernetes-azure>`),
then the `az acs create` command already created two
storage accounts in the same location and resource group
as your Kubernetes cluster.
Both should have the same "storage account SKU": ``Standard_LRS``.
Standard storage is lower-cost and lower-performance.
It uses hard disk drives (HDD).
LRS means locally-redundant storage: three replicas
in the same data center.
Premium storage is higher-cost and higher-performance.
It uses solid state drives (SSD).
At the time of writing,
when we created a storage account with SKU ``Premium_LRS``
and tried to use that,
the PersistentVolumeClaim would get stuck in a "Pending" state.
For future reference, the command to create a storage account is
`az storage account create <https://docs.microsoft.com/en-us/cli/azure/storage/account#create>`_.


The Kubernetes template for configuration of Storage Class is located in the
file ``mongodb/mongo-sc.yaml``.

You may have to update the ``parameters.location`` field in the file to
specify the location you are using in Azure.

Create the required storage classes using:

.. code:: bash

   $ kubectl --context k8s-bdb-test-cluster-0 apply -f mongodb/mongo-sc.yaml


You can check if it worked using ``kubectl get storageclasses``.

**Azure.** Note that there is no line of the form
``storageAccount: <azure storage account name>``
under ``parameters:``. When we included one
and then created a PersistentVolumeClaim based on it,
the PersistentVolumeClaim would get stuck
in a "Pending" state.
Kubernetes just looks for a storageAccount
with the specified skuName and location.


Step 10: Create Kubernetes Persistent Volume Claims
---------------------------------------------------

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

   $ kubectl --context k8s-bdb-test-cluster-0 apply -f mongodb/mongo-pvc.yaml


You can check its status using: ``kubectl get pvc -w``

Initially, the status of persistent volume claims might be "Pending"
but it should become "Bound" fairly quickly.


Step 11: Start a Kubernetes StatefulSet for MongoDB
---------------------------------------------------

  * This configuration is located in the file ``mongodb/mongo-ss.yaml``.

  * Set the ``spec.serviceName`` to the value set in ``mdb-instance-name`` in
    the ConfigMap.
    For example, if the value set in the ``mdb-instance-name``
    is ``mdb-instance-0``, set the field to ``mdb-instance-0``.
  
  * Set ``metadata.name``, ``spec.template.metadata.name`` and
    ``spec.template.metadata.labels.app`` to the value set in
    ``mdb-instance-name`` in the ConfigMap, followed by
    ``-ss``.
    For example, if the value set in the
    ``mdb-instance-name`` is ``mdb-instance-0``, set the fields to the value
    ``mdb-insance-0-ss``.

  * Note how the MongoDB container uses the ``mongo-db-claim`` and the
    ``mongo-configdb-claim`` PersistentVolumeClaims for its ``/data/db`` and
    ``/data/configdb`` directories (mount paths).
    
  * Note also that we use the pod's ``securityContext.capabilities.add``
    specification to add the ``FOWNER`` capability to the container. That is
    because the MongoDB container has the user ``mongodb``, with uid ``999`` and
    group ``mongodb``, with gid ``999``.
    When this container runs on a host with a mounted disk, the writes fail
    when there is no user with uid ``999``. To avoid this, we use the Docker
    feature of ``--cap-add=FOWNER``. This bypasses the uid and gid permission
    checks during writes and allows data to be persisted to disk.
    Refer to the `Docker docs
    <https://docs.docker.com/engine/reference/run/#runtime-privilege-and-linux-capabilities>`_
    for details.

  * As we gain more experience running MongoDB in testing and production, we
    will tweak the ``resources.limits.cpu`` and ``resources.limits.memory``.

  * Create the MongoDB StatefulSet using:

    .. code:: bash

       $ kubectl --context k8s-bdb-test-cluster-0 apply -f mongodb/mongo-ss.yaml
   
  * It might take up to 10 minutes for the disks, specified in the Persistent
    Volume Claims above, to be created and attached to the pod.
    The UI might show that the pod has errored with the message
    "timeout expired waiting for volumes to attach/mount". Use the CLI below
    to check the status of the pod in this case, instead of the UI.
    This happens due to a bug in Azure ACS.
   
    .. code:: bash

       $ kubectl --context k8s-bdb-test-cluster-0 get pods -w
  

Step 12: Configure Users and Access Control for MongoDB
-------------------------------------------------------

  * In this step, you will create a user on MongoDB with authorization
    to create more users and assign
    roles to them.
    Note: You need to do this only when setting up the first MongoDB node of
    the cluster.

  * Find out the name of your MongoDB pod by reading the output
    of the ``kubectl ... get pods`` command at the end of the last step.
    It should be something like ``mdb-instance-0-ss-0``.
  
  * Log in to the MongoDB pod using:

    .. code:: bash

       $ kubectl --context k8s-bdb-test-cluster-0 exec -it <name of your MongoDB pod> bash
  
  * Open a mongo shell using the certificates
    already present at ``/etc/mongod/ssl/``

    .. code:: bash
     
       $ mongo --host localhost --port 27017 --verbose --ssl \
         --sslCAFile /etc/mongod/ssl/ca.pem \
         --sslPEMKeyFile /etc/mongod/ssl/mdb-instance.pem

  * Initialize the replica set using:
    
    .. code:: bash
    
       > rs.initiate( {
           _id : "bigchain-rs",
           members: [ {
             _id : 0,
             host  :"<hostname>:27017"
           } ]
         } )

    The ``hostname`` in this case will be the value set in
    ``mdb-instance-name`` in the ConfigMap.
    For example, if the value set in the ``mdb-instance-name`` is
    ``mdb-instance-0``, set the ``hostname`` above to the value ``mdb-instance-0``.
  
  * The instance should be voted as the ``PRIMARY`` in the replica set (since
    this is the only instance in the replica set till now).
    This can be observed from the mongo shell prompt,
    which will read ``PRIMARY>``.

  * Create a user ``adminUser`` on the ``admin`` database with the
    authorization to create other users. This will only work the first time you
    log in to the mongo shell. For further details, see `localhost
    exception <https://docs.mongodb.com/manual/core/security-users/#localhost-exception>`_
    in MongoDB.
    
    .. code:: bash
    
       PRIMARY> use admin
       PRIMARY> db.createUser( {
                  user: "adminUser",
                  pwd: "superstrongpassword",
                  roles: [ { role: "userAdminAnyDatabase", db: "admin" } ]
                } )

  * Exit and restart the mongo shell using the above command.
    Authenticate as the ``adminUser`` we created earlier:

    .. code:: bash

       PRIMARY> use admin
       PRIMARY> db.auth("adminUser", "superstrongpassword")

  * We need to specify the user name *as seen in the certificate* issued to
    the BigchainDB instance in order to authenticate correctly. Use
    the following ``openssl`` command to extract the user name from the
    certificate:

    .. code:: bash

       $ openssl x509 -in <path to the bigchaindb certificate> \
         -inform PEM -subject -nameopt RFC2253

    You should see an output line that resembles:
    
    .. code:: bash
    
       subject= emailAddress=dev@bigchaindb.com,CN=test-bdb-ssl,OU=BigchainDB-Instance,O=BigchainDB GmbH,L=Berlin,ST=Berlin,C=DE

    The ``subject`` line states the complete user name we need to use for
    creating the user on the mongo shell as follows:

    .. code:: bash
    
       PRIMARY> db.getSiblingDB("$external").runCommand( {
                  createUser: 'emailAddress=dev@bigchaindb.com,CN=test-bdb-ssl,OU=BigchainDB-Instance,O=BigchainDB GmbH,L=Berlin,ST=Berlin,C=DE',
                  writeConcern: { w: 'majority' , wtimeout: 5000 },
                  roles: [
                    { role: 'clusterAdmin', db: 'admin' },
                    { role: 'readWriteAnyDatabase', db: 'admin' }
                  ]
                } )

  * You can similarly create users for MongoDB Monitoring Agent and MongoDB
    Backup Agent. For example:

    .. code:: bash

       PRIMARY> db.getSiblingDB("$external").runCommand( {
                  createUser: 'emailAddress=dev@bigchaindb.com,CN=test-mdb-mon-ssl,OU=MongoDB-Mon-Instance,O=BigchainDB GmbH,L=Berlin,ST=Berlin,C=DE',
                  writeConcern: { w: 'majority' , wtimeout: 5000 },
                  roles: [
                    { role: 'clusterMonitor', db: 'admin' }
                  ]
                } )

       PRIMARY> db.getSiblingDB("$external").runCommand( {
                  createUser: 'emailAddress=dev@bigchaindb.com,CN=test-mdb-bak-ssl,OU=MongoDB-Bak-Instance,O=BigchainDB GmbH,L=Berlin,ST=Berlin,C=DE',
                  writeConcern: { w: 'majority' , wtimeout: 5000 },
                  roles: [
                    { role: 'backup',    db: 'admin' }
                  ]
                } )


Step 13: Start a Kubernetes Deployment for MongoDB Monitoring Agent
-------------------------------------------------------------------

  * This configuration is located in the file
    ``mongodb-monitoring-agent/mongo-mon-dep.yaml``.

  * Set ``metadata.name``, ``spec.template.metadata.name`` and
    ``spec.template.metadata.labels.app`` to the value set in
    ``mdb-mon-instance-name`` in the ConfigMap, followed by
    ``-dep``.
    For example, if the value set in the
    ``mdb-mon-instance-name`` is ``mdb-mon-instance-0``, set the fields to the
    value ``mdb-mon-instance-0-dep``.

  * Start the Kubernetes Deployment using:

    .. code:: bash

       $ kubectl --context k8s-bdb-test-cluster-0 apply -f mongodb-monitoring-agent/mongo-mon-dep.yaml


Step 14: Start a Kubernetes Deployment for MongoDB Backup Agent
---------------------------------------------------------------

  * This configuration is located in the file
    ``mongodb-backup-agent/mongo-backup-dep.yaml``.

  * Set ``metadata.name``, ``spec.template.metadata.name`` and
    ``spec.template.metadata.labels.app`` to the value set in
    ``mdb-bak-instance-name`` in the ConfigMap, followed by
    ``-dep``.
    For example, if the value set in the
    ``mdb-bak-instance-name`` is ``mdb-bak-instance-0``, set the fields to the
    value ``mdb-bak-instance-0-dep``.

  * Start the Kubernetes Deployment using:

    .. code:: bash

       $ kubectl --context k8s-bdb-test-cluster-0 apply -f mongodb-backup-agent/mongo-backup-dep.yaml


Step 15: Start a Kubernetes Deployment for Bigchaindb
-----------------------------------------------------

  * This configuration is located in the file
    ``bigchaindb/bigchaindb-dep.yaml``.

  * Set ``metadata.name`` and ``spec.template.metadata.labels.app`` to the
    value set in ``bdb-instance-name`` in the ConfigMap, followed by
    ``-dep``.
    For example, if the value set in the
    ``bdb-instance-name`` is ``bdb-instance-0``, set the fields to the
    value ``bdb-insance-0-dep``.

  * Set ``BIGCHAINDB_DATABASE_HOST`` to the value set in ``mdb-instance-name``
    in the ConfigMap.
    For example, if the value set in the ``mdb-instance-name`` is
    ``mdb-instance-0``, set the field to the value ``mdb-instance-0``.
   
  * Set the appropriate ``BIGCHAINDB_KEYPAIR_PUBLIC``,
    ``BIGCHAINDB_KEYPAIR_PRIVATE`` values.
   
  * One way to generate BigchainDB keypair is to run a Python shell with
    the command
    ``from bigchaindb_driver import crypto; crypto.generate_keypair()``.
   
  * As we gain more experience running BigchainDB in testing and production,
    we will tweak the ``resources.limits`` values for CPU and memory, and as
    richer monitoring and probing becomes available in BigchainDB, we will
    tweak the ``livenessProbe`` and ``readinessProbe`` parameters.
  
  * Create the BigchainDB Deployment using:

    .. code:: bash

       $ kubectl --context k8s-bdb-test-cluster-0 apply -f bigchaindb/bigchaindb-dep.yaml


  * You can check its status using the command ``kubectl get deploy -w``


Step 16: Configure the MongoDB Cloud Manager
--------------------------------------------

  * Refer to the
    :ref:`documentation <Configure MongoDB Cloud Manager for Monitoring and Backup>`
    for details on how to configure the MongoDB Cloud Manager to enable
    monitoring and backup.


Step 17: Verify the BigchainDB Node Setup
-----------------------------------------

Step 17.1: Testing Internally
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Run a container that provides utilities like ``nslookup``, ``curl`` and ``dig``
on the cluster and query the internal DNS and IP endpoints.

.. code:: bash

   $ kubectl run -it toolbox -- image <docker image to run> --restart=Never --rm

There is a generic image based on alpine:3.5 with the required utilities
hosted at Docker Hub under
`bigchaindb/toolbox <https://hub.docker.com/r/bigchaindb/toolbox/>`_.
The corresponding
`Dockerfile <https://github.com/bigchaindb/bigchaindb/blob/master/k8s/toolbox/Dockerfile>`_
is in the ``bigchaindb/bigchaindb`` repository on GitHub.

You can use it as below to get started immediately:

.. code:: bash

   $ kubectl --context k8s-bdb-test-cluster-0 \
      run -it toolbox \
      --image bigchaindb/toolbox \
      --image-pull-policy=Always \
      --restart=Never --rm

It will drop you to the shell prompt.
Now you can query for the ``mdb`` and ``bdb`` service details.

The ``nslookup`` commands should output the configured IP addresses of the
services in the cluster

The ``dig`` commands should return the port numbers configured for the
various services in the cluster.

Finally, the ``curl`` commands test the availability of the services
themselves.

  * Verify MongoDB instance
    
    .. code:: bash

       $ nslookup mdb-instance-0
        
       $ dig +noall +answer _mdb-port._tcp.mdb-instance-0.default.svc.cluster.local SRV
        
       $ curl -X GET http://mdb-instance-0:27017
    
  * Verify BigchainDB instance
    
    .. code:: bash

       $ nslookup bdb-instance-0
        
       $ dig +noall +answer _bdb-port._tcp.bdb-instance-0.default.svc.cluster.local SRV
        
       $ curl -X GET http://bdb-instance-0:9984
  
  * Verify NGINX instance
    
    .. code:: bash

       $ nslookup ngx-instance-0
        
       $ dig +noall +answer _ngx-public-mdb-port._tcp.ngx-instance-0.default.svc.cluster.local SRV
        
       $ curl -X GET http://ngx-instance-0:27017 # results in curl: (56) Recv failure: Connection reset by peer
        
       $ dig +noall +answer _ngx-public-bdb-port._tcp.ngx-instance-0.default.svc.cluster.local SRV
  
  * If you have run the vanilla NGINX instance, run

    .. code:: bash

       $ curl -X GET http://ngx-instance-0:80
  
  * If you have the OpenResty NGINX + 3scale instance, run

    .. code:: bash

       $ curl -X GET https://ngx-instance-0
  
  * Check the MongoDB monitoring and backup agent on the MongoDB Cloud Manager
    portal to verify they are working fine.
  
  * Send some transactions to BigchainDB and verify it's up and running!


Step 17.2: Testing Externally
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Try to access the ``<dns/ip of your exposed bigchaindb service endpoint>:80``
on your browser. You must receive a json output that shows the BigchainDB
server version among other things.

Use the Python Driver to send some transactions to the BigchainDB node and
verify that your node or cluster works as expected.

