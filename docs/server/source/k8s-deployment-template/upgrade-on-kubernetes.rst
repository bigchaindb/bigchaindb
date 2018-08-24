
.. Copyright BigchainDB GmbH and BigchainDB contributors
   SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
   Code is Apache-2.0 and docs are CC-BY-4.0

Kubernetes Template: Upgrade all Software in a BigchainDB Node
==============================================================

.. note::

   A highly-available Kubernetes cluster requires at least five virtual machines
   (three for the master and two for your app's containers).
   Therefore we don't recommend using Kubernetes to run a BigchainDB node
   if that's the only thing the Kubernetes cluster will be running.
   Instead, see our :ref:`simple-deployment-template`.
   If your organization already *has* a big Kubernetes cluster running many containers,
   and your organization has people who know Kubernetes,
   then this Kubernetes deployment template might be helpful.

This page outlines how to upgrade all the software associated
with a BigchainDB node running on Kubernetes,
including host operating systems, Docker, Kubernetes,
and BigchainDB-related software.


Upgrade Host OS, Docker and Kubernetes
--------------------------------------

Some Kubernetes installation & management systems
can do full or partial upgrades of host OSes, Docker,
or Kubernetes, e.g.
`Tectonic <https://coreos.com/tectonic/>`_, 
`Rancher <https://docs.rancher.com/rancher/v1.5/en/>`_,
and 
`Kubo <https://pivotal.io/kubo>`_.
Consult the documentation for your system.

**Azure Container Service (ACS).**
On Dec. 15, 2016, a Microsoft employee
`wrote <https://github.com/colemickens/azure-kubernetes-status/issues/15#issuecomment-267453251>`_:
"In the coming months we [the Azure Kubernetes team] will be building managed updates in the ACS service."
At the time of writing, managed updates were not yet available,
but you should check the latest
`ACS documentation <https://docs.microsoft.com/en-us/azure/container-service/>`_
to see what's available now.
Also at the time of writing, ACS only supported Ubuntu
as the host (master and agent) operating system.
You can upgrade Ubuntu and Docker on Azure
by SSHing into each of the hosts,
as documented on 
:ref:`another page <ssh-to-your-new-kubernetes-cluster-nodes>`.

In general, you can SSH to each host in your Kubernetes Cluster
to update the OS and Docker.

.. note::

   Once you are in an SSH session with a host,
   the ``docker info`` command is a handy way to detemine the
   host OS (including version) and the Docker version.

When you want to upgrade the software on a Kubernetes node,
you should "drain" the node first,
i.e. tell Kubernetes to gracefully terminate all pods
on the node and mark it as unscheduleable
(so no new pods get put on the node during its downtime).

.. code::

   kubectl drain $NODENAME

There are `more details in the Kubernetes docs <https://kubernetes.io/docs/concepts/cluster-administration/cluster-management/#maintenance-on-a-node>`_,
including instructions to make the node scheduleable again.

To manually upgrade the host OS,
see the docs for that OS.

To manually upgrade Docker, see
`the Docker docs <https://docs.docker.com/>`_.

To manually upgrade all Kubernetes software in your Kubernetes cluster, see
`the Kubernetes docs <https://kubernetes.io/docs/admin/cluster-management/>`_.


Upgrade BigchainDB-Related Software
-----------------------------------

We use Kubernetes "Deployments" for NGINX, BigchainDB,
and most other BigchainDB-related software.
The only exception is MongoDB; we use a Kubernetes
StatefulSet for that.

The nice thing about Kubernetes Deployments
is that Kubernetes can manage most of the upgrade process.
A typical upgrade workflow for a single Deployment would be:

.. code::

   $ KUBE_EDITOR=nano kubectl edit deployment/<name of Deployment>

The ``kubectl edit`` command
opens the specified editor (nano in the above example),
allowing you to edit the specified Deployment *in the Kubernetes cluster*.
You can change the version tag on the Docker image, for example. 
Don't forget to save your edits before exiting the editor.
The Kubernetes docs have more information about
`Deployments <https://kubernetes.io/docs/concepts/workloads/controllers/deployment/>`_ (including updating them).


The upgrade story for the MongoDB StatefulSet is *different*.
(This is because MongoDB has persistent state,
which is stored in some storage associated with a PersistentVolumeClaim.)
At the time of writing, StatefulSets were still in beta,
and they did not support automated image upgrade (Docker image tag upgrade).
We expect that to change.
Rather than trying to keep these docs up-to-date,
we advise you to check out the current
`Kubernetes docs about updating containers in StatefulSets
<https://kubernetes.io/docs/tutorials/stateful-application/basic-stateful-set/#updating-containers>`_.


