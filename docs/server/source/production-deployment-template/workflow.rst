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

1. :doc:`Deploy a Kubernetes cluster on Azure <../production-deployment-template/template-kubernetes-azure>`.

2. Make up an FQDN for your BigchainDB node (e.g. ``mynode.mycorp.com``).
Make sure you've registered the associated domain name (e.g. ``mycorp.com``),
and have an SSL certificate for the FQDN.
(You can get an SSL certificate from any SSL certificate provider.)

3. Download the HTTPS certificate chain and HTTPS certificate key of your registered domain.
Certificate chain includes your primary SSL cert (e.g. your_domain.crt) followed by all intermediate and root
CA cert(s). e.g. If cert if from DigiCert, download "Best format for nginx".

4a. If the BigchainDB node uses 3scale for API authentication, monitoring and billing,
you must ask the BigchainDB node operator/owner for all relevant 3scale credentials and deployment
workflow.

4b. If the BigchainDB does not use 3scale for API authentication, then the organization managing the BigchainDB
node **must** generate a unique *SECRET_TOKEN* for authentication and authorization of requests to the BigchainDB node. 

.. Note::
    All the operations required to set up a Self-Signed CA can be automatically generated from
    our :ref:`"How to configure a BigchainDB node" <how-to-configure-a-bigchaindb-node>` guide.

5. Set Up a Self-Signed Certificate Authority

We use SSL/TLS and self-signed certificates
for MongoDB authentication (and message encryption).
The certificates are signed by the organization managing the :ref:`bigchaindb-node`.

You can now proceed to set up your :ref:`BigchainDB node <kubernetes-template-deploy-a-single-bigchaindb-node>`.
