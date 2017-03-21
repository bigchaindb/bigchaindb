Kubernetes Template: Deploy a Single BigchainDB Node
====================================================

This page describes how to deploy the first BigchainDB node
in a BigchainDB cluster, or a stand-alone BigchainDB node,
using `Kubernetes <https://kubernetes.io/>`_.
It assumes you already have a running Kubernetes cluster.

If you want to add a new BigchainDB node to an existing BigchainDB cluster,
refer to :doc:`the page about that <add-node-on-kubernetes>`.


Step 1: Install kubectl
-----------------------

kubectl is the Kubernetes CLI.
If you don't already have it installed,
then see the `Kubernetes docs to install it
<https://kubernetes.io/docs/user-guide/prereqs/>`_.


Step 2: Configure kubectl
-------------------------

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


Step 3: Create Storage Classes
------------------------------

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

**Azure.** First, you need an Azure storage account.
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


Get the file ``mongo-sc.yaml`` from GitHub using:

.. code:: bash

   $ wget https://raw.githubusercontent.com/bigchaindb/bigchaindb/master/k8s/mongodb/mongo-sc.yaml

You may have to update the ``parameters.location`` field in both the files to
specify the location you are using in Azure.

Create the required storage classes using:

.. code:: bash

   $ kubectl apply -f mongo-sc.yaml


You can check if it worked using ``kubectl get storageclasses``.

**Azure.** Note that there is no line of the form
``storageAccount: <azure storage account name>``
under ``parameters:``. When we included one
and then created a PersistentVolumeClaim based on it,
the PersistentVolumeClaim would get stuck
in a "Pending" state.
Kubernetes just looks for a storageAccount
with the specified skuName and location.


Step 4: Create Persistent Volume Claims
---------------------------------------

Next, you will create two PersistentVolumeClaim objects ``mongo-db-claim`` and
``mongo-configdb-claim``.
Get the file ``mongo-pvc.yaml`` from GitHub using:

.. code:: bash

   $ wget https://raw.githubusercontent.com/bigchaindb/bigchaindb/master/k8s/mongodb/mongo-pvc.yaml

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

   $ kubectl apply -f mongo-pvc.yaml


You can check its status using: ``kubectl get pvc -w``

Initially, the status of persistent volume claims might be "Pending"
but it should become "Bound" fairly quickly.


Step 5: Create the Config Map - Optional
----------------------------------------

This step is required only if you are planning to set up multiple
`BigchainDB nodes
<https://docs.bigchaindb.com/en/latest/terminology.html#node>`_.

MongoDB reads the local ``/etc/hosts`` file while bootstrapping a replica set
to resolve the hostname provided to the ``rs.initiate()`` command. It needs to
ensure that the replica set is being initialized in the same instance where
the MongoDB instance is running.

To achieve this, you will create a ConfigMap with the FQDN of the MongoDB instance
and populate the ``/etc/hosts`` file with this value so that a replica set can
be created seamlessly.

Get the file ``mongo-cm.yaml`` from GitHub using:

.. code:: bash

   $ wget https://raw.githubusercontent.com/bigchaindb/bigchaindb/master/k8s/mongodb/mongo-cm.yaml

You may want to update the ``data.fqdn`` field in the file before creating the
ConfigMap. ``data.fqdn`` field will be the DNS name of your MongoDB instance.
This will be used by other MongoDB instances when forming a MongoDB
replica set. It should resolve to the MongoDB instance in your cluster when
you are done with the setup. This will help when you are adding more MongoDB
instances to the replica set in the future.


**Azure.** 
In Kubernetes on ACS, the name you populate in the ``data.fqdn`` field
will be used to configure a DNS name for the public IP assigned to the
Kubernetes Service that is the frontend for the MongoDB instance.
We suggest using a name that will already be available in Azure.
We use ``mdb-instance-0``, ``mdb-instance-1`` and so on in this document,
which gives us ``mdb-instance-0.<azure location>.cloudapp.azure.com``,
``mdb-instance-1.<azure location>.cloudapp.azure.com``, etc. as the FQDNs.
The ``<azure location>`` is the Azure datacenter location you are using,
which can also be obtained using the ``az account list-locations`` command.
You can also try to assign a name to an Public IP in Azure before starting
the process, or use ``nslookup`` with the name you have in mind to check
if it's available for use.

You should ensure that the the name specified in the ``data.fqdn`` field is
a unique one.

**Kubernetes on bare-metal or other cloud providers.**
You need to provide the name resolution function
by other means (using DNS providers like GoDaddy, CloudFlare or your own
private DNS server). The DNS set up for other environments is currently
beyond the scope of this document.


Create the required ConfigMap using:

.. code:: bash

   $ kubectl apply -f mongo-cm.yaml


You can check its status using: ``kubectl get cm``

Now you are ready to run MongoDB and BigchainDB on our Kubernetes cluster.


Step 6: Run MongoDB as a StatefulSet
------------------------------------

Get the file ``mongo-ss.yaml`` from GitHub using:

.. code:: bash

   $ wget https://raw.githubusercontent.com/bigchaindb/bigchaindb/master/k8s/mongodb/mongo-ss.yaml


Note how the MongoDB container uses the ``mongo-db-claim`` and the
``mongo-configdb-claim`` PersistentVolumeClaims for its ``/data/db`` and
``/data/configdb`` diretories (mount path). Note also that we use the pod's
``securityContext.capabilities.add`` specification to add the ``FOWNER``
capability to the container.
That is because MongoDB container has the user ``mongodb``, with uid ``999``
and group ``mongodb``, with gid ``999``.
When this container runs on a host with a mounted disk, the writes fail when
there is no user with uid ``999``.
To avoid this, we use the Docker feature of ``--cap-add=FOWNER``.
This bypasses the uid and gid permission checks during writes and allows data
to be persisted to disk.
Refer to the
`Docker docs <https://docs.docker.com/engine/reference/run/#runtime-privilege-and-linux-capabilities>`_
for details.

As we gain more experience running MongoDB in testing and production, we will
tweak the ``resources.limits.cpu`` and ``resources.limits.memory``.
We will also stop exposing port ``27017`` globally and/or allow only certain
hosts to connect to the MongoDB instance in the future.

Create the required StatefulSet using:

.. code:: bash

   $ kubectl apply -f mongo-ss.yaml

You can check its status using the commands ``kubectl get statefulsets -w``
and ``kubectl get svc -w``

You may have to wait for up to 10 minutes for the disk to be created
and attached on the first run. The pod can fail several times with the message
saying that the timeout for mounting the disk was exceeded.


Step 7: Initialize a MongoDB Replica Set - Optional
---------------------------------------------------

This step is required only if you are planning to set up multiple
`BigchainDB nodes
<https://docs.bigchaindb.com/en/latest/terminology.html#node>`_.


Login to the running MongoDB instance and access the mongo shell using:

.. code:: bash
   
   $ kubectl exec -it mdb-0 -c mongodb -- /bin/bash
   root@mdb-0:/# mongo --port 27017

You will initiate the replica set by using the ``rs.initiate()`` command from the
mongo shell. Its syntax is:

.. code:: bash

    rs.initiate({ 
        _id : "<replica-set-name",
        members: [ { 
          _id : 0,
          host : "<fqdn of this instance>:<port number>"
        } ]
    })

An example command might look like:

.. code:: bash
   
   > rs.initiate({ _id : "bigchain-rs", members: [ { _id : 0, host :"mdb-instance-0.westeurope.cloudapp.azure.com:27017" } ] })


where ``mdb-instance-0.westeurope.cloudapp.azure.com`` is the value stored in
the ``data.fqdn`` field in the ConfigMap created using ``mongo-cm.yaml``.


You should see changes in the mongo shell prompt from ``>``
to ``bigchain-rs:OTHER>`` to ``bigchain-rs:SECONDARY>`` and finally
to ``bigchain-rs:PRIMARY>``.

You can use the ``rs.conf()`` and the ``rs.status()`` commands to check the
detailed replica set configuration now.


Step 8: Create a DNS record - Optional
--------------------------------------

This step is required only if you are planning to set up multiple
`BigchainDB nodes
<https://docs.bigchaindb.com/en/latest/terminology.html#node>`_.

**Azure.** Select the current Azure resource group and look for the ``Public IP``
resource. You should see at least 2 entries there - one for the Kubernetes
master and the other for the MongoDB instance. You may have to ``Refresh`` the
Azure web page listing the resources in a resource group for the latest
changes to be reflected.
Select the ``Public IP`` resource that is attached to your service (it should
have the Kubernetes cluster name along with a random string),
select ``Configuration``, add the DNS name that was added in the
ConfigMap earlier, click ``Save``, and wait for the changes to be applied.

To verify the DNS setting is operational, you can run ``nslookup <dns
name added in ConfigMap>`` from your local Linux shell.

This will ensure that when you scale the replica set later, other MongoDB
members in the replica set can reach this instance.


Step 9: Run BigchainDB as a Deployment
--------------------------------------

Get the file ``bigchaindb-dep.yaml`` from GitHub using:

.. code:: bash

   $ wget https://raw.githubusercontent.com/bigchaindb/bigchaindb/master/k8s/bigchaindb/bigchaindb-dep.yaml

Note that we set the ``BIGCHAINDB_DATABASE_HOST`` to ``mdb-svc`` which is the
name of the MongoDB service defined earlier.

We also hardcode the ``BIGCHAINDB_KEYPAIR_PUBLIC``,
``BIGCHAINDB_KEYPAIR_PRIVATE`` and ``BIGCHAINDB_KEYRING`` for now.

As we gain more experience running BigchainDB in testing and production, we
will tweak the ``resources.limits`` values for CPU and memory, and as richer
monitoring and probing becomes available in BigchainDB, we will tweak the
``livenessProbe`` and ``readinessProbe`` parameters.

We also plan to specify scheduling policies for the BigchainDB deployment so
that we ensure that BigchainDB and MongoDB are running in separate nodes, and
build security around the globally exposed port ``9984``.

Create the required Deployment using:

.. code:: bash

   $ kubectl apply -f bigchaindb-dep.yaml

You can check its status using the command ``kubectl get deploy -w``


Step 10: Run NGINX as a Deployment
----------------------------------

NGINX is used as a proxy to both the BigchainDB and MongoDB instances in the
node.
It proxies HTTP requests on port 80 to the BigchainDB backend, and TCP
connections on port 27017 to the MongoDB backend.

You can also configure a whitelist in NGINX to allow only connections from
other instances in the MongoDB replica set to access the backend MongoDB
instance.

Get the file ``nginx-cm.yaml`` from GitHub using:

.. code:: bash
   
   $ wget https://raw.githubusercontent.com/bigchaindb/bigchaindb/master/k8s/nginx/nginx-cm.yaml

The IP address whitelist can be explicitly configured in ``nginx-cm.yaml``
file. You will need a list of the IP addresses of all the other MongoDB 
instances in the cluster. If the MongoDB intances specify a hostname, then this
needs to be resolved to the corresponding IP addresses. If the IP address of
any MongoDB instance changes, we can start a 'rolling upgrade' of NGINX after
updating the corresponding ConfigMap without affecting availabilty.


Create the ConfigMap for the whitelist using:

.. code:: bash
   
   $ kubectl apply -f nginx-cm.yaml

Get the file ``nginx-dep.yaml`` from GitHub using:

.. code:: bash
   
   $ wget https://raw.githubusercontent.com/bigchaindb/bigchaindb/master/k8s/nginx/nginx-dep.yaml

Create the NGINX deployment using:

.. code:: bash
   
   $ kubectl apply -f nginx-dep.yaml


Step 11: Verify the BigchainDB Node Setup
-----------------------------------------

Step 11.1: Testing Internally
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Run a container that provides utilities like ``nslookup``, ``curl`` and ``dig``
on the cluster and query the internal DNS and IP endpoints.

.. code:: bash

   $ kubectl run -it toolbox -- image <docker image to run> --restart=Never --rm

There is a generic image based on alpine:3.5 with the required utilities
hosted at Docker Hub under ``bigchaindb/toolbox``.
The corresponding Dockerfile is `here
<https://github.com/bigchaindb/bigchaindb/k8s/toolbox/Dockerfile>`_.

You can use it as below to get started immediately:

.. code:: bash

   $ kubectl run -it toolbox --image bigchaindb/toolbox --restart=Never --rm

It will drop you to the shell prompt.
Now you can query for the ``mdb`` and ``bdb`` service details.

.. code:: bash

   # nslookup mdb-svc
   # nslookup bdb-svc
   # nslookup ngx-svc
   # dig +noall +answer _mdb-port._tcp.mdb-svc.default.svc.cluster.local SRV
   # dig +noall +answer _bdb-port._tcp.bdb-svc.default.svc.cluster.local SRV
   # dig +noall +answer _ngx-public-mdb-port._tcp.ngx-svc.default.svc.cluster.local SRV
   # dig +noall +answer _ngx-public-bdb-port._tcp.ngx-svc.default.svc.cluster.local SRV
   # curl -X GET http://mdb-svc:27017
   # curl -X GET http://bdb-svc:9984
   # curl -X GET http://ngx-svc:80
   # curl -X GET http://ngx-svc:27017

The ``nslookup`` commands should output the configured IP addresses of the
services in the cluster

The ``dig`` commands should return the port numbers configured for the
various services in the cluster.

Finally, the ``curl`` commands test the availability of the services
themselves.

Step 11.2: Testing Externally
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Try to access the ``<dns/ip of your exposed bigchaindb service endpoint>:80``
on your browser. You must receive a json output that shows the BigchainDB
server version among other things.

Try to access the ``<dns/ip of your exposed mongodb service endpoint>:27017``
on your browser. If your IP is in the whitelist, you will receive a message
from the MongoDB instance stating that it doesn't allow HTTP connections to
the port anymore. If your IP is not in the whitelist, your access will be
blocked and you will not see any response from the MongoDB instance.

