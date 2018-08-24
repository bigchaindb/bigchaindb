
.. Copyright BigchainDB GmbH and BigchainDB contributors
   SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
   Code is Apache-2.0 and docs are CC-BY-4.0

Walkthrough: Deploy a Kubernetes Cluster on Azure using Tectonic by CoreOS
==========================================================================

.. note::

   A highly-available Kubernetes cluster requires at least five virtual machines
   (three for the master and two for your app's containers).
   Therefore we don't recommend using Kubernetes to run a BigchainDB node
   if that's the only thing the Kubernetes cluster will be running.
   Instead, see our :ref:`simple-deployment-template`.
   If your organization already *has* a big Kubernetes cluster running many containers,
   and your organization has people who know Kubernetes,
   then this Kubernetes deployment template might be helpful.

A BigchainDB node can be run inside a `Kubernetes <https://kubernetes.io/>`_
cluster.
This page describes one way to deploy a Kubernetes cluster on Azure using Tectonic.
Tectonic helps in easier cluster management of Kubernetes clusters.

If you would rather use Azure Container Service to manage Kubernetes Clusters,
please read :doc:`our guide for that <template-kubernetes-azure>`.


Step 1: Prerequisites for Deploying Tectonic Cluster
----------------------------------------------------

Get an Azure account. Refer to
:ref:`this step in our docs <get-a-pay-as-you-go-azure-subscription>`.

Create an SSH Key pair for the new Tectonic cluster. Refer to
:ref:`this step in our docs <create-an-ssh-key-pair>`.


Step 2: Get a Tectonic Subscription
-----------------------------------

CoreOS offers Tectonic for free for up to 10 nodes.

Sign up for an account `here <https://coreos.com/tectonic>`__ if you do not
have one already and get a license for 10 nodes.

Login to your account, go to Overview > Your Account and save the
``CoreOS License`` and the ``Pull Secret`` to your local machine.


Step 3: Deploy the cluster on Azure
-----------------------------------

The latest instructions for deployment can be found
`here <https://coreos.com/tectonic/docs/latest/tutorials/azure/install.html>`__.

The following points suggests some customizations for a BigchainDB deployment
when following the steps above:


#. Set the ``CLUSTER`` variable to the name of the cluster. Also note that the
   cluster will be deployed in a resource group named 
   ``tectonic-cluster-CLUSTER``.

#. Set the ``tectonic_base_domain`` to ``""`` if you want to use Azure managed
   DNS. You will be assigned a ``cloudapp.azure.com`` sub-domain by default and
   you can skip the ``Configuring Azure DNS`` section from the Tectonic installation
   guide.
   
#. Set the ``tectonic_cl_channel`` to ``"stable"`` unless you want to
   experiment or test with the latest release.

#. Set the ``tectonic_cluster_name`` to the ``CLUSTER`` variable defined in
   the step above.

#. Set the ``tectonic_license_path`` and ``tectonic_pull_secret_path`` to the
   location where you have stored the ``tectonic-license.txt`` and the 
   ``config.json`` files downloaded in the previous step.

#. Set the ``tectonic_etcd_count`` to ``"3"``, so that you have a multi-node
   etcd cluster that can tolerate a single node failure.

#. Set the ``tectonic_etcd_tls_enabled`` to ``"true"`` as this will enable TLS
   connectivity between the etcd nodes and their clients.

#. Set the ``tectonic_master_count`` to ``"3"`` so that you cane tolerate a
   single master failure.

#. Set the ``tectonic_worker_count`` to ``"2"``.

#. Set the ``tectonic_azure_location`` to ``"westeurope"`` if you want to host
   the cluster in Azure's ``westeurope`` datacenter.

#. Set the ``tectonic_azure_ssh_key`` to the path of the public key created in
   the previous step.

#. We recommend setting up or using a CA(Certificate Authority) to generate Tectonic
   Console's server certificate(s) and adding it to your trusted authorities on the client side,
   accessing the Tectonic Console i.e. Browser. If you already have a CA(self-signed or otherwise),
   Set the ``tectonic_ca_cert`` and ``tectonic_ca_key`` configurations with the content
   of PEM-encoded certificate and key files, respectively. For more information about, how to set
   up a self-signed CA, Please refer to
   :doc:`How to Set up self-signed CA <ca-installation>`.

#. Note that the ``tectonic_azure_client_secret`` is the same as the
   ``ARM_CLIENT_SECRET``.

#. Note that the URL for the Tectonic console using these settings will be the
   cluster name set in the configutation file, the datacenter name and
   ``cloudapp.azure.com``. For example, if you named your cluster as 
   ``test-cluster`` and specified the datacenter as ``westeurope``, the Tectonic
   console will be available at ``test-cluster.westeurope.cloudapp.azure.com``.

#. Note that, if you do not specify ``tectonic_ca_cert``, a CA certificate will
   be generated automatically and you will encounter the untrusted certificate
   message on your client(Browser), when accessing the Tectonic Console.


Step 4: Configure kubectl
-------------------------

#. Refer to `this tutorial
   <https://coreos.com/tectonic/docs/latest/tutorials/azure/first-app.html>`__
   for instructions on how to download the kubectl configuration files for
   your cluster.

#. Set the ``KUBECONFIG`` environment variable to make ``kubectl`` use the new
   config file along with the existing configuration.

.. code:: bash

    $ export KUBECONFIG=$HOME/.kube/config:/path/to/config/kubectl-config
    
    # OR to only use the new configuration, try

    $ export KUBECONFIG=/path/to/config/kubectl-config

Next, you can follow one of our following deployment templates:

* :doc:`node-on-kubernetes`.


Tectonic References
-------------------

#. https://coreos.com/tectonic/docs/latest/tutorials/azure/install.html
#. https://coreos.com/tectonic/docs/latest/troubleshooting/installer-terraform.html
#. https://coreos.com/tectonic/docs/latest/tutorials/azure/first-app.html