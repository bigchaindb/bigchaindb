How to Generate a Client Certificate for MongoDB
================================================

This page enumerates the steps *we* use to generate a client certificate to be
used by clients who want to connect to a TLS-secured MongoDB cluster.
We use Easy-RSA.


Step 1: Install and Configure Easy-RSA
--------------------------------------

First create a directory for the client certificate and cd into it:

.. code:: bash

   mkdir client-cert

   cd client-cert

Then :ref:`install and configure Easy-RSA in that directory <How to Install & Configure Easy-RSA>`.


Step 2: Create the Client Private Key and CSR
---------------------------------------------

You can create the client private key and certificate signing request (CSR)
by going into the directory ``client-cert/easy-rsa-3.0.1/easyrsa``
and using:

.. code:: bash
        
   ./easyrsa init-pki

   ./easyrsa gen-req bdb-instance-0 nopass

You should change ``bdb-instance-0`` to a value that reflects what the 
client certificate is being used for.

Tip: You can get help with the ``easyrsa`` command (and its subcommands)
by using the subcommand ``./easyrsa help``


Step 3: Get the Client Certificate Signed
-----------------------------------------

The CSR file (created in the previous step)
should be located in ``pki/reqs/bdb-instance-0.req``.
You need to send it to the organization managing the cluster
so that they can use their CA
to sign the request.
(The managing organization should already have a self-signed CA.)

If you are the admin of the managing organization's self-signed CA,
then you can import the CSR and use Easy-RSA to sign it. For example:

.. code:: bash
        
   ./easyrsa import-req bdb-instance-0.req bdb-instance-0

   ./easyrsa sign-req client bdb-instance-0
        
Once you have signed it, you can send the signed certificate
and the CA certificate back to the requestor.
The files are ``pki/issued/bdb-instance-0.crt`` and ``pki/ca.crt``.


Step 4: Generate the Consolidated Client PEM File
-------------------------------------------------

MongoDB requires a single, consolidated file containing both the public and
private keys.

.. code:: bash
        
   cat bdb-instance-0.crt bdb-instance-0.key > bdb-instance-0.pem
