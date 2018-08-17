
.. Copyright BigchainDB GmbH and BigchainDB contributors
   SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
   Code is Apache-2.0 and docs are CC-BY-4.0

How to Revoke an SSL/TLS Certificate
====================================

This page enumerates the steps *we* take to revoke a self-signed SSL/TLS
certificate in a BigchainDB network.
It can only be done by someone with access to the self-signed CA
associated with the network's managing organization.

Step 1: Revoke a Certificate
----------------------------

Since we used Easy-RSA version 3 to
:ref:`set up the CA <how-to-set-up-a-self-signed-certificate-authority>`,
we use it to revoke certificates too.

Go to the following directory (associated with the self-signed CA):
``.../bdb-node-ca/easy-rsa-3.0.1/easyrsa3``.
You need to be aware of the file name used to import the certificate using the
``./easyrsa import-req`` before. Run the following command to revoke a
certificate:

.. code:: bash

   ./easyrsa revoke <filename>


This will update the CA database with the revocation details.
The next step is to use the updated database to issue an up-to-date
certificate revocation list (CRL).

Step 2: Generate a New CRL
--------------------------

Generate a new CRL for your infrastructure using:

.. code:: bash
        
   ./easyrsa gen-crl

The generated ``crl.pem`` file needs to be uploaded to your infrastructure to
prevent the revoked certificate from being used again.

In particlar, the generated ``crl.pem`` file should be sent to all BigchainDB node operators in your BigchainDB network, so that they can update it in their MongoDB instance and their BigchainDB Server instance.
