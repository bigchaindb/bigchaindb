How to Set Up a Self-Signed Certificate Authority
=================================================

This page enumerates the steps *we* use to set up a self-signed certificate authority (CA).
This is something that only needs to be done once per cluster,
by the organization managing the cluster, i.e. the CA is for the whole cluster.
We use Easy-RSA.


Step 1: Install & Configure Easy-RSA
------------------------------------

First create a directory for the CA and cd into it:

.. code:: bash

   mkdir bdb-cluster-ca

   cd bdb-cluster-ca

Then :ref:`install and configure Easy-RSA in that directory <How to Install & Configure Easy-RSA>`.


Step 2: Create a Self-Signed CA
-------------------------------

You can create a self-signed CA
by going to the ``bdb-cluster-ca/easy-rsa-3.0.1/easyrsa3`` directory and using:

.. code:: bash
        
   ./easyrsa init-pki
        
   ./easyrsa build-ca

You will be prompted to enter the Distinguished Name for this CA. You can hit
enter to accept the default values or change it at each prompt.

You will also be asked to enter a PEM pass phrase for encrypting the ``ca.key`` file.
Make sure to securely store that PEM pass phrase.
If you lose it, you won't be able to add or remove entities from your PKI infrastructure in the future.

It will ask several other questions.
You can accept all the defaults [in brackets] by pressing Enter.
While ``Easy-RSA CA`` *is* a valid and acceptable Common Name,
you should probably enter a name based on the name of the managing organization,
e.g. ``Omega Ledger CA``.

Tip: You can get help with the ``easyrsa`` command (and its subcommands)
by using the subcommand ``./easyrsa help``


Step 3: Create an Intermediate CA
---------------------------------

TODO(Krish)

Step 4: Generate a Certificate Revocation List
----------------------------------------------

You can generate a Certificate Revocation List (CRL) using:

.. code:: bash
        
   ./easyrsa gen-crl

You will need to run this command every time you revoke a certificate and the
generated ``crl.pem`` needs to be uploaded to your infrastructure to prevent
the revoked certificate from being used again.


Step 5: Secure the CA
---------------------

The security of your infrastructure depends on the security of this CA.

- Ensure that you restrict access to the CA and enable only legitimate and
  required people to sign certificates and generate CRLs.

- Restrict access to the machine where the CA is hosted.

- Many certificate providers keep the CA offline and use a rotating
  intermediate CA to sign and revoke certificates, to mitigate the risk of the
  CA getting compromised.

- In case you want to destroy the machine where you created the CA
  (for example, if this was set up on a cloud provider instance),
  you can backup the entire ``easyrsa`` directory
  to secure storage. You can always restore it to a trusted instance again
  during the times when you want to sign or revoke certificates.
  Remember to backup the directory after every update.
