Overview
========

This page summarizes the steps *we* go through
to set up a production BigchainDB + Tendermint cluster.
We are constantly improving them.
You can modify them to suit your needs.

.. Note::
    With our BigchainDB + Tendermint deployment model, we use standalone MongoDB
    (without Replica Set), BFT replication is handled by Tendermint.


1. Set Up a Self-Signed Certificate Authority
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We use SSL/TLS and self-signed certificates
for MongoDB authentication (and message encryption).
The certificates are signed by the organization managing the :ref:`bigchaindb-node`.
If your organization already has a process
for signing certificates
(i.e. an internal self-signed certificate authority [CA]),
then you can skip this step.
Otherwise, your organization must
:ref:`set up its own self-signed certificate authority <how-to-set-up-a-self-signed-certificate-authority>`.


.. _register-a-domain-and-get-an-ssl-certificate-for-it-tmt:

2. Register a Domain and Get an SSL Certificate for It
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The BigchainDB APIs (HTTP API and WebSocket API) should be served using TLS,
so the organization running the cluster
should choose an FQDN for their API (e.g. api.organization-x.com),
register the domain name,
and buy an SSL/TLS certificate for the FQDN.

.. _things-each-node-operator-must-do-tmt:

Things Each Node Operator Must Do
---------------------------------

- [ ] Use a standard and unique naming convention for all instances.

#. Name of the MongoDB instance (``mdb-instance-*``)
#. Name of the BigchainDB instance (``bdb-instance-*``)
#. Name of the NGINX instance (``ngx-http-instance-*`` or ``ngx-https-instance-*``)
#. Name of the OpenResty instance (``openresty-instance-*``)
#. Name of the MongoDB monitoring agent instance (``mdb-mon-instance-*``)
#. Name of the Tendermint instance (``tendermint-instance-*``)

Example
^^^^^^^

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
      "tendermint-instance-1",
      "tendermint-instance-2",
      "tendermint-instance-3",
      "tendermint-instance-4"
    ]
  }


☐ Generate three keys and corresponding certificate signing requests (CSRs):

#. Server Certificate for the MongoDB instance
#. Client Certificate for BigchainDB Server to identify itself to MongoDB
#. Client Certificate for MongoDB Monitoring Agent to identify itself to MongoDB

Use the self-signed CA to sign those three CSRs:

* Three certificates (one for each CSR).

For help, see the pages:

* :doc:`How to Generate a Server Certificate for MongoDB <../production-deployment-template/server-tls-certificate>`
* :doc:`How to Generate a Client Certificate for MongoDB <../production-deployment-template/client-tls-certificate>`

☐ Make up an FQDN for your BigchainDB node (e.g. ``mynode.mycorp.com``).
Make sure you've registered the associated domain name (e.g. ``mycorp.com``),
and have an SSL certificate for the FQDN.
(You can get an SSL certificate from any SSL certificate provider.)

☐ Ask the managing organization for the user name to use for authenticating to
MongoDB.

☐ If the cluster uses 3scale for API authentication, monitoring and billing,
you must ask the managing organization for all relevant 3scale credentials -
secret token, service ID, version header and API service token.

☐ If the cluster uses MongoDB Cloud Manager for monitoring,
you must ask the managing organization for the ``Project ID`` and the
``Agent API Key``.
(Each Cloud Manager "Project" has its own ``Project ID``. A ``Project ID`` can
contain a number of ``Agent API Key`` s. It can be found under
**Settings**. It was recently added to the Cloud Manager to
allow easier periodic rotation of the ``Agent API Key`` with a constant
``Project ID``)


.. _generate-the-blockchain-id-and-genesis-time:

3. Generate the Blockchain ID and Genesis Time
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Tendermint nodes require two parameters that need to be common and shared between all the
participants in the network.

* ``chain_id`` : ID of the blockchain. This must be unique for every blockchain.

  * Example: ``0001-01-01T00:00:00Z``

* ``genesis_time`` : Official time of blockchain start.

  * Example: ``test-chain-9gHylg``

The following parameters can be generated using the ``tendermint init`` command.
To `initializae <https://tendermint.readthedocs.io/en/master/using-tendermint.html#initialize>`_.
You will need to `install Tendermint <https://tendermint.readthedocs.io/en/master/install.html>`_
and verify that a ``genesis.json`` file in created under the `Root Directory
<https://tendermint.readthedocs.io/en/master/using-tendermint.html#directory-root>`_. You can use
the ``genesis_time`` and ``chain_id`` from this ``genesis.json``.

Sample ``genesis.json``:

.. code:: json

    {
    "genesis_time": "0001-01-01T00:00:00Z",
    "chain_id": "test-chain-9gHylg",
    "validators": [
        {
        "pub_key": {
            "type": "ed25519",
            "data": "D12279E746D3724329E5DE33A5AC44D5910623AA6FB8CDDC63617C959383A468"
        },
        "power": 10,
        "name": ""
        }
    ],
    "app_hash": ""
    }



☐ :doc:`Deploy a Kubernetes cluster on Azure <../production-deployment-template/template-kubernetes-azure>`.

☐ You can now proceed to set up your :ref:`BigchainDB node
<kubernetes-template-deploy-a-single-bigchaindb-node-with-tendermint>`.
