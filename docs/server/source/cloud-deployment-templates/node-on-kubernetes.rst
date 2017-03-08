Run a BigchainDB Node in a Kubernetes Cluster
=============================================

Assuming you already have a `Kubernetes <https://kubernetes.io/>`_
cluster up and running, this page describes how to run a
BigchainDB node in it.


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


Step 3: Create a StorageClass
-----------------------------

MongoDB needs somewhere to store its data persistently,
outside the container where MongoDB is running.
Explaining how Kubernetes handles persistent volumes,
and the associated terminology,
is beyond the scope of this documentation;
see `the Kubernetes docs about persistent volumes
<https://kubernetes.io/docs/user-guide/persistent-volumes>`_.

The first thing to do is create a Kubernetes StorageClass.

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

Create a Kubernetes Storage Class named ``slow``
by writing a file named ``azureStorageClass.yml`` containing:

.. code:: yaml

   kind: StorageClass
   apiVersion: storage.k8s.io/v1beta1
   metadata:
     name: slow
   provisioner: kubernetes.io/azure-disk
   parameters:
     skuName: Standard_LRS
     location: <region where your cluster is located>

and then:

.. code:: bash

   $ kubectl apply -f azureStorageClass.yml

You can check if it worked using ``kubectl get storageclasses``.

Note that there is no line of the form
``storageAccount: <azure storage account name>``
under ``parameters:``. When we included one
and then created a PersistentVolumeClaim based on it,
the PersistentVolumeClaim would get stuck
in a "Pending" state.
Kubernetes just looks for a storageAccount
with the specified skuName and location.


Step 4: Create a PersistentVolumeClaim
--------------------------------------

Next, you'll create a PersistentVolumeClaim named ``mongoclaim``.
Create a file named ``mongoclaim.yml``
with the following contents:

.. code:: yaml

   kind: PersistentVolumeClaim
   apiVersion: v1
   metadata:
     name: mongoclaim
     annotations:
       volume.beta.kubernetes.io/storage-class: slow
   spec:
     accessModes:
       - ReadWriteOnce
     resources:
       requests:
         storage: 20Gi

Note how there's no explicit mention of Azure, AWS or whatever.
``ReadWriteOnce`` (RWO) means the volume can be mounted as
read-write by a single Kubernetes node.
(``ReadWriteOnce`` is the *only* access mode supported
by AzureDisk.)
``storage: 20Gi`` means the volume has a size of 20
`gibibytes <https://en.wikipedia.org/wiki/Gibibyte>`_.
(You can change that if you like.)

Create ``mongoclaim`` in your Kubernetes cluster:

.. code:: bash

   $ kubectl apply -f mongoclaim.yml

You can check its status using:

.. code:: bash

   $ kubectl get pvc

Initially, the status of ``mongoclaim`` might be "Pending"
but it should become "Bound" fairly quickly.

.. code:: bash

   $ kubectl describe pvc
   Name:            mongoclaim
   Namespace:       default
   StorageClass:    slow
   Status:          Bound
   Volume:          pvc-ebed81f1-fdca-11e6-abf0-000d3a27ab21
   Labels:          <none>
   Capacity:        20Gi
   Access Modes:    RWO
   No events.


Step 5: Deploy MongoDB & BigchainDB
-----------------------------------

Now you can deploy MongoDB and BigchainDB to your Kubernetes cluster.
Currently, the way we do that is we create a StatefulSet with two
containers: BigchainDB and MongoDB. (In the future, we'll put them
in separate pods, and we'll ensure those pods are in different nodes.)
We expose BigchainDB's port 9984 (the HTTP API port)
and MongoDB's port 27017 using a Kubernetes Service.

Get the file ``node-mdb-ss.yaml`` from GitHub using:

.. code:: bash

   $ wget https://raw.githubusercontent.com/bigchaindb/bigchaindb/master/k8s/node-mdb-ss.yaml

Take a look inside that file to see how it defines the Service
and the StatefulSet.
Note how the MongoDB container uses the ``mongoclaim`` PersistentVolumeClaim
for its ``/data`` diretory (mount path).

Create the StatefulSet and Service in your cluster using:

.. code:: bash

   $ kubectl apply -f node-mdb-ss.yaml

You can check that they're working using:

.. code:: bash

   $ kubectl get services
   $ kubectl get statefulsets
