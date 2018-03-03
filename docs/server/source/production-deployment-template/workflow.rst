.. _kubernetes-template-overview:

Overview
========

This page summarizes the steps *we* go through
to set up a production BigchainDB cluster.
We are constantly improving them.
You can modify them to suit your needs.

.. _generate-the-blockchain-id-and-genesis-time:

Generate All Shared Tendermint Setup Parameters
-----------------------------------------------

There are some shared Tendermint setup paramters that every node operator
in the consortium shares
because they are properties of the Tendermint cluster.
They look like this:

.. code::

   # Tendermint data
   TM_SEEDS='tm-instance-1,tm-instance-2,tm-instance-3,tm-instance-4'
   TM_VALIDATORS='tm-instance-1,tm-instance-2,tm-instance-3,tm-instance-4'
   TM_VALIDATOR_POWERS='10,10,10,10'
   TM_GENESIS_TIME='0001-01-01T00:00:00Z'
   TM_CHAIN_ID='test-chain-rwcPML'

Those paramters only have to be generated once, by one member of the consortium.
That person will then share the results (Tendermint setup parameters)
with all the node operators.

The above example parameters are for a cluster of 4 initial (seed) nodes.
Note how ``TM_SEEDS``, ``TM_VALIDATORS`` and ``TM_VALIDATOR_POWERS`` are lists
with 4 items each.
**If your consortium has a different number of initial nodes,
then those lists should have that number or items.**
Use ``10`` for all the power values.

To generate a ``TM_GENESIS_TIME`` and a ``TM_CHAIN_ID``,
you can do this:

.. code::

   $ mkdir $(pwd)/tmdata
   $ docker run --rm -v $(pwd)/tmdata:/tendermint tendermint/tendermint:0.13 init
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

The value with ``"genesis_time"`` is ``TM_GENESIS_TIME`` and
the value with ``"chain_id"`` is ``TM_CHAIN_ID``.

Now you have all the Tendermint setup parameters and can share them
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
Every BigchainDB node in a cluster can have a different secret token.

3. Deploy a Kubernetes cluster for your BigchainDB node. We have some instructions for how to
:doc:`Deploy a Kubernetes cluster on Azure <../production-deployment-template/template-kubernetes-azure>`.

.. warning::

   In theory, you can deploy your BigchainDB node to any Kubernetes cluster, but there can be differences
   between different Kubernetes clusters, especially if they are running different versions of Kubernetes.
   We tested this Production Deployment Template on Azure ACS in February 2018 and at that time
   ACS was deploying a **Kubernetes 1.7.7** cluster. If you can force your cluster to have that version of Kubernetes,
   then you'll increase the likelihood that everything will work in your cluster.

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