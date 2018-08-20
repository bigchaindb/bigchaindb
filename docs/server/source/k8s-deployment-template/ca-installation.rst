
.. Copyright BigchainDB GmbH and BigchainDB contributors
   SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
   Code is Apache-2.0 and docs are CC-BY-4.0

.. _how-to-set-up-a-self-signed-certificate-authority:

How to Set Up a Self-Signed Certificate Authority
=================================================

This page enumerates the steps *we* use to set up a self-signed certificate authority (CA).
This is something that only needs to be done once per BigchainDB network,
by the organization managing the network, i.e. the CA is for the whole network.
We use Easy-RSA.


Step 1: Install & Configure Easy-RSA
------------------------------------

First create a directory for the CA and cd into it:

.. code:: bash

   mkdir bdb-node-ca

   cd bdb-node-ca

Then :ref:`install and configure Easy-RSA in that directory <how-to-install-and-configure-easyrsa>`.


Step 2: Create a Self-Signed CA
-------------------------------

You can create a self-signed CA
by going to the ``bdb-node-ca/easy-rsa-3.0.1/easyrsa3`` directory and using:

.. code:: bash
        
   ./easyrsa init-pki
        
   ./easyrsa build-ca

You will also be asked to enter a PEM pass phrase (for encrypting the ``ca.key`` file).
Make sure to securely store that PEM pass phrase.
If you lose it, you won't be able to add or remove entities from your PKI infrastructure in the future.

You will be prompted to enter the Distinguished Name (DN) information for this CA.
For each field, you can accept the default value [in brackets] by pressing Enter.

.. warning::

   Don't accept the default value of OU (``IT``). Instead, enter the value ``ROOT-CA``.

While ``Easy-RSA CA`` *is* a valid and acceptable Common Name,
you should probably enter a name based on the name of the managing organization,
e.g. ``Omega Ledger CA``.

Tip: You can get help with the ``easyrsa`` command (and its subcommands)
by using the subcommand ``./easyrsa help``


Step 3: Create an Intermediate CA
---------------------------------

TODO

Step 4: Generate a Certificate Revocation List
----------------------------------------------

You can generate a Certificate Revocation List (CRL) using:

.. code:: bash
        
   ./easyrsa gen-crl

You will need to run this command every time you revoke a certificate.
The generated ``crl.pem`` needs to be uploaded to your infrastructure to
prevent the revoked certificate from being used again.


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
