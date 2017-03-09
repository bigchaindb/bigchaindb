Run a BigchainDB Node in a Kubernetes Cluster
=============================================

Assuming you already have a `Kubernetes <https://kubernetes.io/>`_
cluster up and running, this page describes how to run a
BigchainDB node in it.

In a nutshell, kubernetes consists of ``basic kubernetes objects`` - Pod,
Service, Volume, Namespace - and ``controllers`` that are built using basic
objects - ReplicaSet, Deployment, StatefulSet, DaemonSet, Job


Step 1: Install kubectl
-----------------------

kubectl is the Kubernetes CLI.

.. code:: bash

   $ curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl
   $ chmod +x ./kubectl
   $ sudo mv ./kubectl /usr/local/bin/kubectl
   $ . <(kubectl completion bash) # auto-completion



Step 2: Configure kubectl
-------------------------

The default location of the kubectl configuration file is ``~/.kube/config``.
If you don't have that file, then you need to get it.

If you deployed your Kubernetes cluster on Azure
using the Azure CLI 2.0 (as per :doc:`our template <template-kubernetes-azure>`),
then you can get the ``~/.kube/config`` file using:

.. code:: bash

   $ az acs kubernetes get-credentials \
   --resource-group <name of resource group containing the cluster> \
   --name <ACS cluster name>


Step 3: Run a MongoDB Container 
-------------------------------

To start a MongoDB Docker container in a pod on one of the cluster nodes:

.. code:: bash

   $ kubectl ?????


Note: The BigchainDB Dashboard can be deployed
as a Docker container, like everything else.
