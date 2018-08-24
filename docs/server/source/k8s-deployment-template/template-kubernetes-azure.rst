
.. Copyright BigchainDB GmbH and BigchainDB contributors
   SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
   Code is Apache-2.0 and docs are CC-BY-4.0

Template: Deploy a Kubernetes Cluster on Azure
==============================================

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
This page describes one way to deploy a Kubernetes cluster on Azure.


.. _get-a-pay-as-you-go-azure-subscription:

Step 1: Get a Pay-As-You-Go Azure Subscription
----------------------------------------------

Microsoft Azure has a Free Trial subscription (at the time of writing),
but it's too limited to run an advanced BigchainDB node.
Sign up for a Pay-As-You-Go Azure subscription
via `the Azure website <https://azure.microsoft.com>`_.

You may find that you have to sign up for a Free Trial subscription first.
That's okay: you can have many subscriptions.


.. _create-an-ssh-key-pair:

Step 2: Create an SSH Key Pair
------------------------------

You'll want an SSH key pair so you'll be able to SSH
to the virtual machines that you'll deploy in the next step.
(If you already have an SSH key pair, you *could* reuse it,
but it's probably a good idea to make a new SSH key pair
for your Kubernetes VMs and nothing else.)

See the
:doc:`page about how to generate a key pair for SSH
<../appendices/generate-key-pair-for-ssh>`.


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

If you already *have* the Azure CLI installed, you may want to update it.

.. warning::

   ``az component update`` isn't supported if you installed the CLI using some of Microsoft's provided installation instructions. See `the Microsoft docs for update instructions <https://docs.microsoft.com/en-us/cli/azure/install-az-cli2>`_.


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
   --master-count 3 \
   --agent-count 3 \
   --admin-username ubuntu \
   --agent-vm-size Standard_L4s \
   --dns-prefix <make up a name> \
   --ssh-key-value ~/.ssh/<name>.pub \
   --orchestrator-type kubernetes \
   --debug --output json

.. Note::
    The `Azure documentation <https://docs.microsoft.com/en-us/cli/azure/acs?view=azure-cli-latest#az_acs_create>`_
    has a list of all ``az acs create`` options.
    You might prefer a smaller agent VM size, for example.
    You can also get a list of the options using:

    .. code:: bash

       $ az acs create --help


It takes a few minutes for all the resources to deploy.
You can watch the progress in the `Azure Portal
<https://portal.azure.com>`_:
go to **Resource groups** (with the blue cube icon)
and click on the one you created
to see all the resources in it.


Trouble with the Service Principal? Then Read This!
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If the ``az acs create`` command fails with an error message including the text,
"The Service Principal in ServicePrincipalProfile could not be validated",
then we found you can prevent that by creating a Service Principal ahead of time
and telling ``az acs create`` to use that one. (It's supposed to create one,
but sometimes that fails, I guess.)

Create a new resource group, even if you created one before. They're free anyway:

.. code:: bash

   $ az login
   $ az group create --name <new resource group name> \
                     --location <Azure region like westeurope>

Note the ``id`` in the output. It looks like
``"/subscriptions/369284be-0104-421a-8488-1aeac0caecbb/resourceGroups/examplerg"``.
It can be copied into the next command.
Create a Service Principal using:

.. code:: bash

   $ az ad sp create-for-rbac --role="Contributor" \
   --scopes=<id value copied from above, including the double quotes on the ends>

Note the ``appId`` and ``password``.
Put those in a new ``az acs create`` command like above, with two new options added:

.. code:: bash

   $ az acs create ... \
   --service-principal <appId> \
   --client-secret <password>


.. _ssh-to-your-new-kubernetes-cluster-nodes:

Optional: SSH to Your New Kubernetes Cluster Nodes
--------------------------------------------------

You can SSH to one of the just-deployed Kubernetes "master" nodes
(virtual machines) using:

.. code:: bash

   $ ssh -i ~/.ssh/<name> ubuntu@<master-ip-address-or-fqdn>

where you can get the IP address or FQDN
of a master node from the Azure Portal. For example:

.. code:: bash

   $ ssh -i ~/.ssh/mykey123 ubuntu@mydnsprefix.westeurope.cloudapp.azure.com

.. note::

   All the master nodes are accessible behind the *same* public IP address and
   FQDN. You connect to one of the masters randomly based on the load balancing
   policy.

The "agent" nodes shouldn't get public IP addresses or externally accessible
FQDNs, so you can't SSH to them *directly*,
but you can first SSH to the master
and then SSH to an agent from there using their hostname.
To do that, you could
copy your SSH key pair to the master (a bad idea),
or use SSH agent forwarding (better).
To do the latter, do the following on the machine you used
to SSH to the master:

.. code:: bash

   $ echo -e "Host <FQDN of the cluster from Azure Portal>\n  ForwardAgent yes" >> ~/.ssh/config

To verify that SSH agent forwarding works properly,
SSH to the one of the master nodes and do:

.. code:: bash

   $ echo "$SSH_AUTH_SOCK"

If you get an empty response,
then SSH agent forwarding hasn't been set up correctly.
If you get a non-empty response,
then SSH agent forwarding should work fine
and you can SSH to one of the agent nodes (from a master)
using:

.. code:: bash

   $ ssh ubuntu@k8s-agent-4AC80E97-0

where ``k8s-agent-4AC80E97-0`` is the name
of a Kubernetes agent node in your Kubernetes cluster.
You will have to replace it by the name
of an agent node in your cluster.


Optional: Delete the Kubernetes Cluster
---------------------------------------

.. code:: bash

   $ az acs delete \
   --name <ACS cluster name> \
   --resource-group <name of resource group containing the cluster>


Optional: Delete the Resource Group
-----------------------------------

CAUTION: You might end up deleting resources other than the ACS cluster.

.. code:: bash

   $ az group delete \
   --name <name of resource group containing the cluster>


Next, you can :doc:`run a BigchainDB node/cluster(BFT) <node-on-kubernetes>`
on your new Kubernetes cluster.
