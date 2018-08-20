
.. Copyright BigchainDB GmbH and BigchainDB contributors
   SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
   Code is Apache-2.0 and docs are CC-BY-4.0

.. _how-to-generate-a-client-certificate-for-mongodb:

How to Generate a Client Certificate for MongoDB
================================================

This page enumerates the steps *we* use to generate a client certificate to be
used by clients who want to connect to a TLS-secured MongoDB database.
We use Easy-RSA.


Step 1: Install and Configure Easy-RSA
--------------------------------------

First create a directory for the client certificate and cd into it:

.. code:: bash

   mkdir client-cert

   cd client-cert

Then :ref:`install and configure Easy-RSA in that directory <how-to-install-and-configure-easyrsa>`.


Step 2: Create the Client Private Key and CSR
---------------------------------------------

You can create the client private key and certificate signing request (CSR)
by going into the directory ``client-cert/easy-rsa-3.0.1/easyrsa3``
and using:

.. code:: bash

   ./easyrsa init-pki

   ./easyrsa gen-req bdb-instance-0 nopass

You should change the Common Name (e.g. ``bdb-instance-0``)
to a value that reflects what the
client certificate is being used for, e.g. ``mdb-mon-instance-3`` or ``mdb-bak-instance-4``. (The final integer is specific to your BigchainDB node in the BigchainDB network.)

You will be prompted to enter the Distinguished Name (DN) information for this certificate. For each field, you can accept the default value [in brackets] by pressing Enter.

.. warning::

   Don't accept the default value of OU (``IT``). Instead, enter the value
   ``BigchainDB-Instance``, ``MongoDB-Mon-Instance`` or ``MongoDB-Backup-Instance``
   as appropriate.

Aside: The ``nopass`` option means "do not encrypt the private key (default is encrypted)". You can get help with the ``easyrsa`` command (and its subcommands)
by using the subcommand ``./easyrsa help``.

.. note::
    For more information about requirements for MongoDB client certificates, please consult the `official MongoDB
    documentation <https://docs.mongodb.com/manual/tutorial/configure-x509-client-authentication/>`_.


Step 3: Get the Client Certificate Signed
-----------------------------------------

The CSR file created in the previous step
should be located in ``pki/reqs/bdb-instance-0.req``
(or whatever Common Name you used in the ``gen-req`` command above).
You need to send it to the organization managing the BigchainDB network
so that they can use their CA
to sign the request.
(The managing organization should already have a self-signed CA.)

If you are the admin of the managing organization's self-signed CA,
then you can import the CSR and use Easy-RSA to sign it.
Go to your ``bdb-node-ca/easy-rsa-3.0.1/easyrsa3/``
directory and do something like:

.. code:: bash

   ./easyrsa import-req /path/to/bdb-instance-0.req bdb-instance-0

   ./easyrsa sign-req client bdb-instance-0

Once you have signed it, you can send the signed certificate
and the CA certificate back to the requestor.
The files are ``pki/issued/bdb-instance-0.crt`` and ``pki/ca.crt``.


Step 4: Generate the Consolidated Client PEM File
-------------------------------------------------

.. note::
    This step can be skipped for BigchainDB client certificate as BigchainDB
    uses the PyMongo driver, which accepts separate certificate and key files.

MongoDB, MongoDB Backup Agent and MongoDB Monitoring Agent require a single,
consolidated file containing both the public and private keys.

.. code:: bash

   cat /path/to/bdb-instance-0.crt /path/to/bdb-instance-0.key > bdb-instance-0.pem

    OR

   cat /path/to/mdb-mon-instance-0.crt /path/to/mdb-mon-instance-0.key > mdb-mon-instance-0.pem

    OR

   cat /path/to/mdb-bak-instance-0.crt /path/to/mdb-bak-instance-0.key > mdb-bak-instance-0.pem
