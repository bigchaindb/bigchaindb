Advanced Node on Azure
======================

.. note::

   This page is a work in progress.

This page describes how to deploy an "advanced BigchainDB node"
on Microsoft Azure; advanced because it uses Docker containers,
multiple virtual machines, and `Kubernetes <https://kubernetes.io/>`_
for container orchestration.


Step 1: Get a Pay-As-You-Go Azure Subscription
----------------------------------------------

Microsoft Azure has a Free Trial subscription (at the time of writing),
but it's too limited to run an advanced BigchainDB node.
Sign up for a Pay-As-You-Go Azure subscription
via `the Azure website <https://azure.microsoft.com>`_.

You may find that you have to sign up for a Free Trial subscription first.
That's okay: you can have many subscriptions.


Step 2: Deploy an Azure Container Service (ACS)
-----------------------------------------------

It's *possible* to deploy an Azure Container Service (ACS)
from the `Azure Portal <https://portal.azure.com>`_
(i.e. online in your web browser)
but it's actually easier to do it using the Azure
Command-Line Interface (CLI).
(The Azure Portal will ask you for a public SSH key
and a "service principal," and you'll have to create those
first if they don't exist. The CLI will create them
for you if necessary.)

Microsoft has `instructions to install the Azure CLI 2.0
on most common operating systems
<https://docs.microsoft.com/en-us/cli/azure/install-az-cli2>`_.
Do that.

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
   --generate-ssh-keys \
   --location <same location as the resource group> \
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

