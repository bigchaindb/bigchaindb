
.. Copyright BigchainDB GmbH and BigchainDB contributors
   SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
   Code is Apache-2.0 and docs are CC-BY-4.0

.. _how-to-generate-a-server-certificate-for-mongodb:

How to Generate a Server Certificate for MongoDB
================================================

This page enumerates the steps *we* use to generate a
server certificate for a MongoDB instance.
A server certificate is also referred to as a "member certificate"
in the MongoDB documentation.
We use Easy-RSA.


Step 1: Install & Configure Easy–RSA
------------------------------------

First create a directory for the server certificate (member cert) and cd into it:

.. code:: bash

   mkdir member-cert

   cd member-cert

Then :ref:`install and configure Easy-RSA in that directory <how-to-install-and-configure-easyrsa>`.


Step 2: Create the Server Private Key and CSR
---------------------------------------------

You can create the server private key and certificate signing request (CSR)
by going into the directory ``member-cert/easy-rsa-3.0.1/easyrsa3``
and using something like:

.. note::

    Please make sure you are fullfilling the requirements for `MongoDB server/member certificates
    <https://docs.mongodb.com/manual/tutorial/configure-x509-member-authentication>`_.

.. code:: bash

   ./easyrsa init-pki

   ./easyrsa --req-cn=mdb-instance-0 --subject-alt-name=DNS:localhost,DNS:mdb-instance-0 gen-req mdb-instance-0 nopass

You should replace the Common Name (``mdb-instance-0`` above) with the correct name for *your* MongoDB instance in the network, e.g. ``mdb-instance-5`` or ``mdb-instance-12``. (This name is decided by the organization managing the network.)

You will be prompted to enter the Distinguished Name (DN) information for this certificate.
For each field, you can accept the default value [in brackets] by pressing Enter.

.. warning::

   Don't accept the default value of OU (``IT``). Instead, enter the value ``MongoDB-Instance``.

Aside: You need to provide the ``DNS:localhost`` SAN during certificate generation
for using the ``localhost exception`` in the MongoDB instance.
All certificates can have this attribute without compromising security as the
``localhost exception`` works only the first time.


Step 3: Get the Server Certificate Signed
-----------------------------------------

The CSR file created in the last step
should be located in ``pki/reqs/mdb-instance-0.req``
(where the integer ``0`` may be different for you).
You need to send it to the organization managing the BigchainDB network
so that they can use their CA
to sign the request.
(The managing organization should already have a self-signed CA.)

If you are the admin of the managing organization's self-signed CA,
then you can import the CSR and use Easy-RSA to sign it.
Go to your ``bdb-node-ca/easy-rsa-3.0.1/easyrsa3/``
directory and do something like:

.. code:: bash

   ./easyrsa import-req /path/to/mdb-instance-0.req mdb-instance-0

   ./easyrsa --subject-alt-name=DNS:localhost,DNS:mdb-instance-0 sign-req server mdb-instance-0

Once you have signed it, you can send the signed certificate
and the CA certificate back to the requestor.
The files are ``pki/issued/mdb-instance-0.crt`` and ``pki/ca.crt``.


Step 4: Generate the Consolidated Server PEM File
-------------------------------------------------

MongoDB requires a single, consolidated file containing both the public and
private keys.

.. code:: bash

   cat /path/to/mdb-instance-0.crt /path/to/mdb-instance-0.key > mdb-instance-0.pem

