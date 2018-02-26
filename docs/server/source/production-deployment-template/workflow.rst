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

☐ Set Up a Self-Signed Certificate Authority

We use SSL/TLS and self-signed certificates
for MongoDB authentication (and message encryption).
The certificates are signed by the organization managing the :ref:`bigchaindb-node`.
If your organization already has a process
for signing certificates
(i.e. an internal self-signed certificate authority [CA]),
then you can skip this step.
Otherwise, your organization must
:ref:`set up its own self-signed certificate authority <how-to-set-up-a-self-signed-certificate-authority>`.


☐ Follow Standard and Unique Naming Convention

  ☐ Name of the MongoDB instance (``mdb-instance-*``)

  ☐ Name of the BigchainDB instance (``bdb-instance-*``)

  ☐ Name of the NGINX instance (``ngx-http-instance-*`` or ``ngx-https-instance-*``)

  ☐ Name of the OpenResty instance (``openresty-instance-*``)

  ☐ Name of the MongoDB monitoring agent instance (``mdb-mon-instance-*``)

  ☐ Name of the Tendermint instance (``tm-instance-*``)

**Example**


.. code:: text

  {
    "MongoDB": [
      "mdb-instance-1",
      "mdb-instance-2",
      "mdb-instance-3",
      "mdb-instance-4"
    ],
    "BigchainDB": [
      "bdb-instance-1",
      "bdb-instance-2",
      "bdb-instance-3",
      "bdb-instance-4"
    ],
    "NGINX": [
      "ngx-instance-1",
      "ngx-instance-2",
      "ngx-instance-3",
      "ngx-instance-4"
    ],
    "OpenResty": [
      "openresty-instance-1",
      "openresty-instance-2",
      "openresty-instance-3",
      "openresty-instance-4"
    ],
    "MongoDB_Monitoring_Agent": [
      "mdb-mon-instance-1",
      "mdb-mon-instance-2",
      "mdb-mon-instance-3",
      "mdb-mon-instance-4"
    ],
    "Tendermint": [
      "tm-instance-1",
      "tm-instance-2",
      "tm-instance-3",
      "tm-instance-4"
    ]
  }


☐ Generate three keys and corresponding certificate signing requests (CSRs):

#. Server Certificate for the MongoDB instance
#. Client Certificate for BigchainDB Server to identify itself to MongoDB
#. Client Certificate for MongoDB Monitoring Agent to identify itself to MongoDB

Use the self-signed CA to sign those three CSRs. For help, see the pages:

* :doc:`How to Generate a Server Certificate for MongoDB <../production-deployment-template/server-tls-certificate>`
* :doc:`How to Generate a Client Certificate for MongoDB <../production-deployment-template/client-tls-certificate>`

☐ Make up an FQDN for your BigchainDB node (e.g. ``mynode.mycorp.com``).
Make sure you've registered the associated domain name (e.g. ``mycorp.com``),
and have an SSL certificate for the FQDN.
(You can get an SSL certificate from any SSL certificate provider.)

☐ Ask the BigchainDB Node operator/owner for the username to use for authenticating to
MongoDB.

☐ If the cluster uses 3scale for API authentication, monitoring and billing,
you must ask the BigchainDB node operator/owner for all relevant 3scale credentials -
secret token, service ID, version header and API service token.

☐ If the cluster uses MongoDB Cloud Manager for monitoring,
you must ask the managing organization for the ``Project ID`` and the
``Agent API Key``.
(Each Cloud Manager "Project" has its own ``Project ID``. A ``Project ID`` can
contain a number of ``Agent API Key`` s. It can be found under
**Settings**. It was recently added to the Cloud Manager to
allow easier periodic rotation of the ``Agent API Key`` with a constant
``Project ID``)


☐ :doc:`Deploy a Kubernetes cluster on Azure <../production-deployment-template/template-kubernetes-azure>`.

☐ You can now proceed to set up your :ref:`BigchainDB node
<kubernetes-template-deploy-a-single-bigchaindb-node>`.
