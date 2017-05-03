Setup a Self-Signed Certificate Authority
=========================================

This document enumerates the steps we recommend to set up a self-hosted or a
self-signed CA.

There are many ways to get this done and you are free to follow the methods
that you are most comfortable with.

We currently use
`easy-rsa version 3
<https://community.openvpn.net/openvpn/wiki/EasyRSA3-OpenVPN-Howto>`_, a 
wrapper over complex ``openssl`` commands and helps us achieve this goal
easily. It is available
`here <https://github.com/OpenVPN/easy-rsa/releases>`_ and licensed under GPLv2.


Step 1: Install Dependencies for CA Setup
-----------------------------------------

The only dependency for easy-rsa v3 is the presence of the ``openssl``
command, which is available from the ``openssl`` package on Ubuntu and other
Debian-based operating systems.

``sudo apt-get install openssl`` should be enough in most cases.


Step 2: Setup the easyrsa Package for CA Setup
----------------------------------------------

Download and extract the latest package.

    .. code:: bash
        
        mkdir federation-ca && cd federation-ca

        wget https://github.com/OpenVPN/easy-rsa/archive/3.0.1.tar.gz

        tar xzvf 3.0.1.tar.gz


This should give you a ``federation-ca/easy-rsa-3.0.1`` directory.


Step 3: Customize the CA Configuration
--------------------------------------

We customize the CA setup by creating a ``vars`` file based on the existing
``vars.example`` file bundled in the package.

The values for the ``Distinguished Name`` given below (country, province,
city, org, email) are references and can be changed as per your
deployment. Refer to the ``vars.example`` file for detailed variable descriptions.

    .. code:: bash
        
        cd easy-rsa-3.0.1/easyrsa3

        cp vars.example vars

        echo 'set_var EASYRSA_DN "org"' >> vars
        echo 'set_var EASYRSA_REQ_OU "BigchainDB Deployment"' >> vars
        echo 'set_var EASYRSA_KEY_SIZE 4096' >> vars
        echo 'set_var EASYRSA_EXT_DIR "$EASYRSA/x509-types"' >> vars
        
        echo 'set_var EASYRSA_REQ_COUNTRY "DE"' >> vars
        echo 'set_var EASYRSA_REQ_PROVINCE "Brandenburg"' >> vars
        echo 'set_var EASYRSA_REQ_CITY "Berlin"' >> vars
        echo 'set_var EASYRSA_REQ_ORG "BigchainDB GmbH"' >> vars
        echo 'set_var EASYRSA_REQ_EMAIL "dev@bigchaindb.com" >> vars


Modify the ``extendedKeyUsage = serverAuth`` to ``extendedKeyUsage =
serverAuth,clientAuth`` in the file x509-types/server.
Refer the MongoDB `documentation <https://docs.mongodb.com/manual/core/security-x.509/>`_ for more details on this.

 
Step 4: Create the Self-Signed CA
---------------------------------

You can create the CA using:

    .. code:: bash
        
        ./easyrsa init-pki
        
        ./easyrsa build-ca


You will be asked to enter a password for encrypting the ``ca.key`` file.
Make sure to securely store this password. If you lose it, you risk not being
able to add or remove entities from your PKI infrastructure in the future.


Step 5: Create an Intermediate CA
---------------------------------

TODO(Krish)

Step 6: Generate a CRL
----------------------

Generate a CRL for your infrastructure using:

    .. code:: bash
        
        ./easyrsa gen-crl

You will need to run this command every time you revoke a certificate and the
generated ``crl.pem`` needs to be uploaded to your infrastructure to prevent
the revoked certificate from being used again.


Step 7: Secure the CA
---------------------


Your PKI infrastructure depends on the security of this CA.

- Ensure that you restrict access to the CA and enable only legitimate and
  required people to sign certificates and generate CRLs.

- Restrict access to the machine where the CA is hosted.

- Many certificate providers keep the CA offline and use a rotating
  intermediate CA to sign and revoke certificates, to mitigate the risk of the
  CA getting compromised.

- In case you want to destroy this machine (for example, if this was set up on
  a cloud provider instance), you can backup the entire ``easyrsa`` directory
  to a secure storage. You can always restore it to a trusted instance again
  during the times when you want to sign or revoke certificates.
  Remember to backup the directory after every update.

