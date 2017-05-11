Set Up a Self-Signed Certificate Authority
==========================================

This page enumerates the steps *we* use to set up a self-signed certificate authority (CA).
Your organization might do it differently.

We use
`Easy-RSA version 3
<https://community.openvpn.net/openvpn/wiki/EasyRSA3-OpenVPN-Howto>`_, a 
wrapper over complex ``openssl`` commands.
`Easy-RSA is available on GitHub <https://github.com/OpenVPN/easy-rsa/releases>`_ and licensed under GPLv2.


Step 1: Install Easy-RSA Dependencies
-------------------------------------

The only dependency for Easy-RSA v3 is the presence of the ``openssl``
command, which is available from the ``openssl`` package on Ubuntu and other
Debian-based operating systems, i.e. you can install it using:

.. code:: bash

   sudo apt-get update

   sudo apt-get install openssl


Step 2: Install Easy-RSA
------------------------

Create a directory named ``federation-ca/easy-rsa-3.0.1``,
then download and extract the latest Easy-RSA package into it:

.. code:: bash
        
   mkdir federation-ca && cd federation-ca

   wget https://github.com/OpenVPN/easy-rsa/archive/3.0.1.tar.gz

   tar xzvf 3.0.1.tar.gz


Step 3: Customize the CA Configuration
--------------------------------------

We customize the CA configuration by creating a ``vars`` file based
on the existing ``vars.example`` file.
The country, province, city, org and email values should be changed 
to the values for your organization.
Refer to the ``vars.example`` file for detailed variable descriptions.

.. code:: bash
        
   cd easy-rsa-3.0.1/easyrsa3

   cp vars.example vars

   echo 'set_var EASYRSA_DN "org"' >> vars
   echo 'set_var EASYRSA_REQ_OU "BigchainDB Deployment"' >> vars
   echo 'set_var EASYRSA_KEY_SIZE 4096' >> vars
   echo 'set_var EASYRSA_EXT_DIR "$EASYRSA/x509-types"' >> vars
        
   echo 'set_var EASYRSA_REQ_COUNTRY "DE"' >> vars
   echo 'set_var EASYRSA_REQ_PROVINCE "Berlin"' >> vars
   echo 'set_var EASYRSA_REQ_CITY "Berlin"' >> vars
   echo 'set_var EASYRSA_REQ_ORG "BigchainDB GmbH"' >> vars
   echo 'set_var EASYRSA_REQ_EMAIL "dev@bigchaindb.com"' >> vars

Edit the file ``x509-types/server`` and change
``extendedKeyUsage = serverAuth`` to 
``extendedKeyUsage = serverAuth,clientAuth``.
See `the MongoDB documentation about x.509 authentication <https://docs.mongodb.com/manual/core/security-x.509/>`_ to understand why.

 
Step 4: Create a Self-Signed CA
-------------------------------

You can create a self-signed CA
by going to the ``federation-ca/easy-rsa-3.0.1/easyrsa3`` directory and using:

.. code:: bash
        
   ./easyrsa init-pki
        
   ./easyrsa build-ca


You will be asked to enter a password for encrypting the ``ca.key`` file.
Make sure to securely store this password. If you lose it, you risk not being
able to add or remove entities in the future.


Step 5: Create an Intermediate CA
---------------------------------

TODO(Krish)

Step 6: Generate a Certificate Revocation List
----------------------------------------------

You can generate a Certificate Revocation List (CRL) using:

.. code:: bash
        
   ./easyrsa gen-crl

You will need to run this command every time you revoke a certificate and the
generated ``crl.pem`` needs to be uploaded to your infrastructure to prevent
the revoked certificate from being used again.


Step 7: Secure the CA
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
