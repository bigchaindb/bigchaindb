How to Generate a Server Certificate for MongoDB
================================================

This page enumerates the steps *we* use to generate a
server certificate for a MongoDB instance.
A server certificate is also referred to as a "member certificate"
in the MongoDB documentation.
We use Easy-RSA.


Step 1: Install & Configure Easy–RSA
------------------------------------

First create a directory for the CA and go into it:

.. code:: bash

   mkdir member-cert

   cd member-cert

Then :ref:`install and configure Easy-RSA in that directory <How to Install & Configure Easy-RSA>`.


Step 2: Create the Server Private Key and CSR
---------------------------------------------

You can create the key and the CSR using:

    .. code:: bash
        
        ./easyrsa init-pki

        ./easyrsa --req-cn=mdb-instance-0 --subject-alt-name=DNS:localhost,DNS:mdb-instance-0 gen-req mdb-instance-0 nopass

You can replace the common name (``mdb-instance-0`` above) with any other name
so long as the instance can verify that it is the hostname.

You need to provide the ``DNS:localhost`` SAN during certificate generation for
using the ``localhost exception`` in MongoDB instance.

All certificates can have this attribute without compromising security as the
``localhost exception`` works only the first time.


Step 3: Sign the Server Certificate
-----------------------------------

The csr file is located in the instance where you ran the above
commands in ``pki/reqs/mdb-instance-0.req``.

You would then need to send this across to the organization which will sign
this request. This will be the self-signed CA that
:ref:`was created earlier <Set Up a Self-Signed Certificate Authority>`.


If you are the federation admin, you can import the csr and sign the
certificate using your easyrsa setup:

    .. code:: bash
        
        ./easyrsa import-req mdb-instance-0.req mdb-instance-0

        ./easyrsa --subject-alt-name=DNS:localhost,DNS:mdb-instance-0 sign-req server mdb-instance-0
        
Once you have signed it, you can send the signed certificate and the CA 
certificate back to the requestor.

The files are ``pki/issued/mdb-instance-0.crt`` and ``pki/ca.crt``.


Step 4: Generate the Consolidated Server PEM File
-------------------------------------------------

MongoDB requires a single, consolidated file containing both the public and
private keys.

    .. code:: bash
        
        cat mdb-instance-0.crt mdb-instance-0.key > mdb-instance-0.pem

The only thing left now is to set the ``net.ssl.PEMKeyFile`` parameter to the
path of the ``mdb-instance-0.pem`` file, and the ``net.ssl.CAFile`` parameter
to the ``ca.crt`` file.
