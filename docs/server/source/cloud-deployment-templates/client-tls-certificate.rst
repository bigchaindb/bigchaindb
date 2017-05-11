Generate Client Certificate for MongoDB
=======================================

This document enumerates the steps we recommend to generate a self-signed
client certificate to be used with clients who want to connect to a TLS
secured MongoDB cluster.

We currently use
`easy-rsa version 3
<https://community.openvpn.net/openvpn/wiki/EasyRSA3-OpenVPN-Howto>`_, a 
wrapper over complex ``openssl`` commands and helps us achieve this goal
easily. It is available
`here <https://github.com/OpenVPN/easy-rsa/releases>`_ and licensed under GPLv2.


Step 1: Install Dependencies for Client Certificate Generation
--------------------------------------------------------------

The only dependency for easy-rsa v3 is the presence of the ``openssl``
command, which is available from the ``openssl`` package on Ubuntu and other
Debian-based operating systems.

``sudo apt-get install openssl`` should be enough in most cases.


Step 2: Setup the easyrsa Package for Client Certificate Generation
-------------------------------------------------------------------

Download and extract the latest package.

    .. code:: bash
        
        mkdir client-cert && cd client-cert

        wget https://github.com/OpenVPN/easy-rsa/archive/3.0.1.tar.gz

        tar xzvf 3.0.1.tar.gz


This should give you a ``client-cert/easy-rsa-3.0.1`` directory.


Step 3: Customize the Configuration for Client Certificate
----------------------------------------------------------

We customize the CA setup by creating a ``vars`` file based on the existing
``vars.example`` file bundled in the package.

The values for the ``Distinguished Name`` given below (country, province,
city, org, email) are references and can be changed as per your
deployment. Refer to the ``vars.example`` file for detailed variable
descriptions.

    .. code:: bash
        
        cd easy-rsa-3.0.1/easyrsa3

        cp vars.example vars

        echo 'set_var EASYRSA_DN "org"' >> vars
        echo 'set_var EASYRSA_REQ_OU "BigchainDB Deployment 1"' >> vars
        echo 'set_var EASYRSA_KEY_SIZE 4096' >> vars
        echo 'set_var EASYRSA_EXT_DIR "$EASYRSA/x509-types"' >> vars
        
        echo 'set_var EASYRSA_REQ_COUNTRY "DE"' >> vars
        echo 'set_var EASYRSA_REQ_PROVINCE "Brandenburg"' >> vars
        echo 'set_var EASYRSA_REQ_CITY "Berlin"' >> vars
        echo 'set_var EASYRSA_REQ_ORG "BigchainDB GmbH"' >> vars
        echo 'set_var EASYRSA_REQ_EMAIL "dev@bigchaindb.com" >> vars


Step 4: Create the Client Private Key and CSR
---------------------------------------------

You can create the key and the CSR using:

    .. code:: bash
        
        ./easyrsa init-pki

        ./easyrsa gen-req bdb-instance-0 nopass


Step 5: Sign the Client Certificate
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


Step 6: Generate the Consolidated Client PEM File
-------------------------------------------------

MongoDB requires a single, consolidated file containing both the public and
private keys.

    .. code:: bash
        
        cat bdb-instance-0.crt bdb-instance-0.key > bdb-instance-0.pem

