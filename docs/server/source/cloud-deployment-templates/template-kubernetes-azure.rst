Template: Deploy a Kubernetes Cluster on Azure
==============================================

A BigchainDB node can be run inside a `Kubernetes <https://kubernetes.io/>`_
cluster.
This page describes one way to deploy a Kubernetes cluster on Azure.


Step 1: Get a Pay-As-You-Go Azure Subscription
----------------------------------------------

Microsoft Azure has a Free Trial subscription (at the time of writing),
but it's too limited to run an advanced BigchainDB node.
Sign up for a Pay-As-You-Go Azure subscription
via `the Azure website <https://azure.microsoft.com>`_.

You may find that you have to sign up for a Free Trial subscription first.
That's okay: you can have many subscriptions.


Step 2: Create an SSH Key Pair
------------------------------

You'll want an SSH key pair so you'll be able to SSH
to the virtual machines that you'll deploy in the next step.
(If you already have an SSH key pair, you *could* reuse it,
but it's probably a good idea to make a new SSH key pair
for your Kubernetes VMs and nothing else.)

See the
:ref:`page about how to generate a key pair for SSH <Generate a Key Pair for SSH>`.


Step 3: Deploy an Azure Container Service (ACS)
-----------------------------------------------

It's *possible* to deploy an Azure Container Service (ACS)
from the `Azure Portal <https://portal.azure.com>`_
(i.e. online in your web browser)
but it's actually easier to do it using the Azure
Command-Line Interface (CLI).

Microsoft has `instructions to install the Azure CLI 2.0
on most common operating systems
<https://docs.microsoft.com/en-us/cli/azure/install-az-cli2>`_.
Do that.

First, update the Azure CLI to the latest version:

.. code:: bash

   $ az component update

Next, login to your account using:

.. code:: bash

   $ az login

It will tell you to open a web page and to copy a code to that page.

If the login is a success, you will see some information
about all your subscriptions, including the one that is currently
enabled (``"state": "Enabled"``). If the wrong one is enabled,
you can switch to the right one using:

.. code:: bash

   $ az account set --subscription <subscription name or ID>

Next, you will have to pick the Azure data center location
where you'd like to deploy your cluster.
You can get a list of all available locations using:

.. code:: bash

   $ az account list-locations

Next, create an Azure "resource group" to contain all the
resources (virtual machines, subnets, etc.) associated
with your soon-to-be-deployed cluster. You can name it
whatever you like but avoid fancy characters because they may
confuse some software.

.. code:: bash

   $ az group create --name <resource group name> --location <location name>

Example location names are ``koreacentral`` and ``westeurope``.

Finally, you can deploy an ACS using something like:

.. code:: bash

   $ az acs create --name <a made-up cluster name> \
   --resource-group <name of resource group created earlier> \
   --agent-count 3 \
   --agent-vm-size Standard_D2_v2 \
   --dns-prefix <make up a name> \
   --ssh-key-value ~/.ssh/<name>.pub \
   --orchestrator-type kubernetes

There are more options. For help understanding all the options, use the built-in help:

.. code:: bash

   $ az acs create --help

It takes a few minutes for all the resources to deploy.
You can watch the progress in the `Azure Portal
<https://portal.azure.com>`_:
go to **Resource groups** (with the blue cube icon)
and click on the one you created
to see all the resources in it.

Next, you can :doc:`run a BigchainDB node on your new
Kubernetes cluster <node-on-kubernetes>`.


Optional: SSH to Your New Kubernetes Cluster Nodes
--------------------------------------------------

You can SSH to one of the just-deployed Kubernetes "master" nodes
(virtual machines) using:

.. code:: bash

   $ ssh -i ~/.ssh/<name>.pub azureuser@<master-ip-address-or-hostname>

where you can get the IP address or hostname
of a master node from the Azure Portal.
Note how the default username is ``azureuser``.

The "agent" nodes don't get public IP addresses or hostnames,
so you can't SSH to them *directly*,
but you can first SSH to the master
and then SSH to an agent from there 
(using the *private* IP address or hostname of the agent node).
To do that, you either need to copy your SSH key pair to
the master (a bad idea),
or use something like
`SSH agent forwarding <https://yakking.branchable.com/posts/ssh-A/>`_ (better).

Next, you can :doc:`run a BigchainDB node on your new
Kubernetes cluster <node-on-kubernetes>`.
