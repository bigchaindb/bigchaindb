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

Then :ref:`install and configure Easy-RSA in that directory <How to Install & Configure Easy-RSA>`.


Step 2: Create the Server Private Key and CSR
---------------------------------------------

You can create the server private key and certificate signing request (CSR)
by going into the directory ``member-cert/easy-rsa-3.0.1/easyrsa``
and using something like:

.. code:: bash
        
   ./easyrsa init-pki

   ./easyrsa --req-cn=mdb-instance-0 --subject-alt-name=DNS:localhost,DNS:mdb-instance-0 gen-req mdb-instance-0 nopass

You will be prompted to enter the Distinguished Name for this certificate. You
can hit enter to accept the default values or change them at each prompt.

You can replace the common name (``mdb-instance-0`` above) with any other name
so long as the instance can verify that it is the hostname.

You need to provide the ``DNS:localhost`` SAN during certificate generation
for using the ``localhost exception`` in the MongoDB instance.

All certificates can have this attribute without compromising security as the
``localhost exception`` works only the first time.


Step 3: Get the Server Certificate Signed
-----------------------------------------

The CSR file (created in the last step)
should be located in ``pki/reqs/mdb-instance-0.req``.
You need to send it to the organization managing the cluster
so that they can use their CA
to sign the request.
(The managing organization should already have a self-signed CA.)

If you are the admin of the managing organization's self-signed CA,
then you can import the CSR and use Easy-RSA to sign it. For example:

.. code:: bash
        
   ./easyrsa import-req mdb-instance-0.req mdb-instance-0

   ./easyrsa --subject-alt-name=DNS:localhost,DNS:mdb-instance-0 sign-req server mdb-instance-0
        
Once you have signed it, you can send the signed certificate
and the CA certificate back to the requestor.
The files are ``pki/issued/mdb-instance-0.crt`` and ``pki/ca.crt``.


Step 4: Generate the Consolidated Server PEM File
-------------------------------------------------

MongoDB requires a single, consolidated file containing both the public and
private keys.

.. code:: bash
        
   cat mdb-instance-0.crt mdb-instance-0.key > mdb-instance-0.pem


Step 5: Update the MongoDB Config File
--------------------------------------

In the MongoDB configuration file, set the ``net.ssl.PEMKeyFile`` parameter to
the path of the ``mdb-instance-0.pem`` file, and the ``net.ssl.CAFile``
parameter to the ``ca.crt`` file.
