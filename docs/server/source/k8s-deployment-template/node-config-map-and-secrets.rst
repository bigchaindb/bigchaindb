
.. Copyright BigchainDB GmbH and BigchainDB contributors
   SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
   Code is Apache-2.0 and docs are CC-BY-4.0

.. _how-to-configure-a-bigchaindb-node:

How to Configure a BigchainDB Node
==================================

.. note::

   A highly-available Kubernetes cluster requires at least five virtual machines
   (three for the master and two for your app's containers).
   Therefore we don't recommend using Kubernetes to run a BigchainDB node
   if that's the only thing the Kubernetes cluster will be running.
   Instead, see our :ref:`simple-deployment-template`.
   If your organization already *has* a big Kubernetes cluster running many containers,
   and your organization has people who know Kubernetes,
   then this Kubernetes deployment template might be helpful.

This page outlines the steps to set a bunch of configuration settings
in your BigchainDB node.
They are pushed to the Kubernetes cluster in two files,
named ``config-map.yaml`` (a set of ConfigMaps)
and ``secret.yaml`` (a set of Secrets).
They are stored in the Kubernetes cluster's key-value store (etcd).

Make sure you did the first four operations listed in the section titled
:ref:`things-each-node-operator-must-do`.


Edit vars
---------

This file is located at: ``k8s/scripts/vars`` and edit
the configuration parameters.
That file already contains many comments to help you
understand each data value, but we make some additional
remarks on some of the values below.


vars.NODE_FQDN
~~~~~~~~~~~~~~~
FQDN for your BigchainDB node. This is the domain name
used to query and access your BigchainDB node. More information can be
found in our :ref:`Kubernetes template overview guide <kubernetes-template-overview>`.


vars.SECRET_TOKEN
~~~~~~~~~~~~~~~~~
This parameter is specific to your BigchainDB node and is used for
authentication and authorization of requests to your BigchainDB node.
More information can be found in our :ref:`Kubernetes template overview guide <kubernetes-template-overview>`.


vars.HTTPS_CERT_KEY_FILE_NAME
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Absolute path of the HTTPS certificate chain of your domain.
More information can be found in our :ref:`Kubernetes template overview guide <kubernetes-template-overview>`.


vars.HTTPS_CERT_CHAIN_FILE_NAME
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Absolute path of the HTTPS certificate key of your domain.
More information can be found in our :ref:`Kubernetes template overview guide <kubernetes-template-overview>`.


vars.MDB_ADMIN_USER and vars.MDB_ADMIN_PASSWORD
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
MongoDB admin user credentials, username and password.
This user is created on the *admin* database with the authorization to create other users.


vars.BDB_PERSISTENT_PEERS, BDB_VALIDATORS, BDB_VALIDATORS_POWERS, BDB_GENESIS_TIME and BDB_CHAIN_ID
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
These parameters are shared across the BigchainDB network. More information about the generation
of these parameters can be found at :ref:`generate-the-blockchain-id-and-genesis-time`.


vars.NODE_DNS_SERVER
^^^^^^^^^^^^^^^^^^^^
IP of Kubernetes service(kube-dns), can be retrieved using
using CLI(kubectl) or k8s dashboard. This parameter is used by the Nginx gateway instance
to resolve the hostnames of all the services running in the Kubernetes cluster.

.. code::

   # retrieval via commandline.
   $ kubectl get services --namespace=kube-system -l k8s-app=kube-dns


.. _generate-config:

Generate configuration
~~~~~~~~~~~~~~~~~~~~~~
After populating the ``k8s/scripts/vars`` file, we need to generate
all the configuration required for the BigchainDB node, for that purpose
we need to execute ``k8s/scripts/generate_configs.sh`` script.

.. code::

   $ bash generate_configs.sh

.. Note::
    During execution the script will prompt the user for some inputs.

After successful execution, this routine will generate ``config-map.yaml`` and
``secret.yaml`` under ``k8s/scripts``.

.. _deploy-config-map-and-secret:

Deploy Your config-map.yaml and secret.yaml
-------------------------------------------

You can deploy your edited ``config-map.yaml`` and ``secret.yaml``
files to your Kubernetes cluster using the commands:

.. code:: bash

   $ kubectl apply -f config-map.yaml

   $ kubectl apply -f secret.yaml
