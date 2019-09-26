
.. Copyright BigchainDB GmbH and BigchainDB contributors
   SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
   Code is Apache-2.0 and docs are CC-BY-4.0

.. _kubernetes-template-overview:

Overview
========

.. note::

   A highly-available Kubernetes cluster requires at least five virtual machines
   (three for the master and two for your app's containers).
   Therefore we don't recommend using Kubernetes to run a BigchainDB node
   if that's the only thing the Kubernetes cluster will be running.
   Instead, see our :ref:`simple-deployment-template`.
   If your organization already *has* a big Kubernetes cluster running many containers,
   and your organization has people who know Kubernetes,
   then this Kubernetes deployment template might be helpful.

This page summarizes some steps to go through
to set up a BigchainDB network.
You can modify them to suit your needs.

.. _generate-the-blockchain-id-and-genesis-time:

Generate All Shared BigchainDB Setup Parameters
-----------------------------------------------

There are some shared BigchainDB setup paramters that every node operator
in the consortium shares
because they are properties of the Tendermint network.
They look like this:

.. code::

   # Tendermint data
   BDB_PERSISTENT_PEERS='bdb-instance-1,bdb-instance-2,bdb-instance-3,bdb-instance-4'
   BDB_VALIDATORS='bdb-instance-1,bdb-instance-2,bdb-instance-3,bdb-instance-4'
   BDB_VALIDATOR_POWERS='10,10,10,10'
   BDB_GENESIS_TIME='0001-01-01T00:00:00Z'
   BDB_CHAIN_ID='test-chain-rwcPML'

Those paramters only have to be generated once, by one member of the consortium.
That person will then share the results (Tendermint setup parameters)
with all the node operators.

The above example parameters are for a network of 4 initial (seed) nodes.
Note how ``BDB_PERSISTENT_PEERS``, ``BDB_VALIDATORS`` and ``BDB_VALIDATOR_POWERS`` are lists
with 4 items each.
**If your consortium has a different number of initial nodes,
then those lists should have that number or items.**
Use ``10`` for all the power values.

To generate a ``BDB_GENESIS_TIME`` and a ``BDB_CHAIN_ID``,
you can do this:

.. code::

   $ mkdir $(pwd)/tmdata
   $ docker run --rm -v $(pwd)/tmdata:/tendermint/config tendermint/tendermint:v0.31.5 init
   $ cat $(pwd)/tmdata/genesis.json

You should see something that looks like:

.. code:: json

   {"genesis_time": "0001-01-01T00:00:00Z",
    "chain_id": "test-chain-bGX7PM",
    "validators": [
        {"pub_key":
            {"type": "ed25519",
             "data": "4669C4B966EB8B99E45E40982B2716A9D3FA53B54C68088DAB2689935D7AF1A9"},
         "power": 10,
         "name": ""}
    ],
    "app_hash": ""
   }

The value with ``"genesis_time"`` is ``BDB_GENESIS_TIME`` and
the value with ``"chain_id"`` is ``BDB_CHAIN_ID``.

Now you have all the BigchainDB setup parameters and can share them
with all of the node operators. (They will put them in their ``vars`` file.
We'll say more about that file below.)


.. _things-each-node-operator-must-do:

Things Each Node Operator Must Do
---------------------------------

1. Make up an `FQDN <https://en.wikipedia.org/wiki/Fully_qualified_domain_name>`_
for your BigchainDB node (e.g. ``mynode.mycorp.com``).
This is where external users will access the BigchainDB HTTP API, for example.
Make sure you've registered the associated domain name (e.g. ``mycorp.com``).

Get an SSL certificate for your BigchainDB node's FQDN.
Also get the root CA certificate and all intermediate certificates.
They should all be provided by your SSL certificate provider.
Put all those certificates together in one certificate chain file in the following order:

- Domain certificate (i.e. the one you ordered for your FQDN)
- All intermediate certificates
- Root CA certificate

DigiCert has `a web page explaining certificate chains <https://www.digicert.com/ssl-support/pem-ssl-creation.htm>`_.

You will put the path to that certificate chain file in the ``vars`` file,
when you configure your node later.

2a. If your BigchainDB node will use 3scale for API authentication, monitoring and billing,
you will need all relevant 3scale settings and credentials.

2b. If your BigchainDB node will not use 3scale, then write authorization will be granted
to all POST requests with a secret token in the HTTP headers.
(All GET requests are allowed to pass.)
You can make up that ``SECRET_TOKEN`` now.
For example, ``superSECRET_token4-POST*requests``.
You will put it in the ``vars`` file later.
Every BigchainDB node in a BigchainDB network can have a different secret token.
To make an HTTP POST request to your BigchainDB node,
you must include an HTTP header named ``X-Secret-Access-Token``
and set it equal to your secret token, e.g.

``X-Secret-Access-Token: superSECRET_token4-POST*requests``


3. Deploy a Kubernetes cluster for your BigchainDB node. We have some instructions for how to
:doc:`Deploy a Kubernetes cluster on Azure <../k8s-deployment-template/template-kubernetes-azure>`.

.. warning::

   In theory, you can deploy your BigchainDB node to any Kubernetes cluster, but there can be differences
   between different Kubernetes clusters, especially if they are running different versions of Kubernetes.
   We tested this Kubernetes Deployment Template on Azure ACS in February 2018 and at that time
   ACS was deploying a **Kubernetes 1.7.7** cluster. If you can force your cluster to have that version of Kubernetes,
   then you'll increase the likelihood that everything will work.

4. Deploy your BigchainDB node inside your new Kubernetes cluster.
You will fill up the ``vars`` file,
then you will run a script which reads that file to generate some Kubernetes config files,
you will send those config files to your Kubernetes cluster,
and then you will deploy all the stuff that you need to have a BigchainDB node.

⟶ Proceed to :ref:`deploy your BigchainDB node <kubernetes-template-deploy-a-single-bigchaindb-node>`.

.. raw:: html

    <br>
    <br>
    <br>
    <br>
    <br>
    <br>
    <br>
    <br>
    <br>
    <br>
    <br>
