
.. Copyright BigchainDB GmbH and BigchainDB contributors
   SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
   Code is Apache-2.0 and docs are CC-BY-4.0

.. _simple-deployment-template:

Simple Deployment Template
==========================

This section describes *one* way to deploy a BigchainDB network
(i.e. a set of connected BigchainDB nodes).
You can modify this simple deployment template as you see fit.
It's "simple" in the sense that each BigchainDB node is installed
and run on a single virtual machine (or real machine).
We also have a :ref:`kubernetes-deployment-template` (not simple).

**Note 1:** These instructions will also work for a "network" with only one node.
If you want your network to be able to handle the failure or misbehavior
of one node, then your network must have at least four nodes.
Nodes can be added or removed from a network after is it up and running.

**Note 2:** If you want to set up a node or network
so that you can contribute to developing and testing the BigchainDB code,
then see
`the docs about contributing to BigchainDB <https://docs.bigchaindb.com/projects/contributing/en/latest/index.html>`_
.

.. toctree::
   :maxdepth: 1

   deploy-a-machine
   set-up-nginx
   set-up-node-software
   network-setup
   tips
   troubleshooting
