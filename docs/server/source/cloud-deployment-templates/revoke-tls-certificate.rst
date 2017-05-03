Revoke a Certificate
====================


This document enumerates the steps needs to revoke a certificate in your PKI
infrastructure.

Since, we had used ``easy-rsa version 3`` to
:ref:`setup the CA <Setup a Self-Signed Certificate Authority>`, we will use it
to revoke certificates too.


Step 1: Revoke a Certificate
----------------------------

You need to be aware of the base filename used to import the certificate, and
run:

    .. code:: bash

        ./easyrsa revoke <filename_base>

This will update the CA database with the revokation details.

The next step is to use this database and issue an up to date CRL.


Step 2: Generate a New CRL
--------------------------

Generate a new CRL for your infrastructure using:

    .. code:: bash
        
        ./easyrsa gen-crl

This generated ``crl.pem`` needs to be uploaded to your infrastructure to
prevent the revoked certificate from being used again.

