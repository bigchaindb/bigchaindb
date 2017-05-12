How to Generate a Client Certificate for MongoDB
================================================

This page enumerates the steps *we* use
to generate a client certificate
to be used by clients who want to connect to a TLS-secured MongoDB cluster.
We use Easy-RSA.


Step 1: Install and Configure Easy-RSA
--------------------------------------

First create a directory for the CA and go into it:

.. code:: bash

   mkdir client-cert

   cd client-cert

Then :ref:`install and configure Easy-RSA in that directory <How to Install & Configure Easy-RSA>`.


Step 2: Create the Client Private Key and CSR
---------------------------------------------

You can create the key and the CSR using:

    .. code:: bash
        
        ./easyrsa init-pki

        ./easyrsa gen-req bdb-instance-0 nopass


Step 3: Sign the Client Certificate
-----------------------------------

The csr file is located in the instance where you ran the above
commands in ``pki/reqs/bdb-instance-0.req``.

You would then need to send this across to the organization which will sign
this request. This will be the self-signed CA that
:ref:`was created earlier <Set Up a Self-Signed Certificate Authority>`.

If you are the federation admin, you can import the csr and sign the
certificate using your easyrsa setup:

    .. code:: bash
        
        ./easyrsa import-req bdb-instance-0.req bdb-instance-0

        ./easyrsa sign-req client bdb-instance-0
        

Once you have signed it, you can send the signed certificate and the CA 
certificate back to the requestor.

The files are ``pki/issued/bdb-instance-0.crt`` and ``pki/ca.crt``.


Step 4: Generate the Consolidated Client PEM File
-------------------------------------------------

MongoDB requires a single, consolidated file containing both the public and
private keys.

    .. code:: bash
        
        cat bdb-instance-0.crt bdb-instance-0.key > bdb-instance-0.pem
