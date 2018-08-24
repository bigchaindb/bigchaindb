
.. Copyright BigchainDB GmbH and BigchainDB contributors
   SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
   Code is Apache-2.0 and docs are CC-BY-4.0

.. _kubernetes-deployment-template:

Kubernetes Deployment Template
==============================

.. note::

   A highly-available Kubernetes cluster requires at least five virtual machines
   (three for the master and two for your app's containers).
   Therefore we don't recommend using Kubernetes to run a BigchainDB node
   if that's the only thing the Kubernetes cluster will be running.
   Instead, see our :ref:`simple-deployment-template`.
   If your organization already *has* a big Kubernetes cluster running many containers,
   and your organization has people who know Kubernetes,
   then this Kubernetes deployment template might be helpful.

This section outlines a way to deploy a BigchainDB node (or BigchainDB network)
on Microsoft Azure using Kubernetes.
You may choose to use it as a template or reference for your own deployment,
but *we make no claim that it is suitable for your purposes*.
Feel free change things to suit your needs or preferences.


.. toctree::
   :maxdepth: 1

   workflow
   ca-installation
   server-tls-certificate
   client-tls-certificate
   revoke-tls-certificate
   template-kubernetes-azure
   node-on-kubernetes
   node-config-map-and-secrets
   log-analytics
   cloud-manager
   easy-rsa
   upgrade-on-kubernetes
   bigchaindb-network-on-kubernetes
   tectonic-azure
   troubleshoot
   architecture
