Generate Cluster Member Certificate for MongoDB
===============================================


This document enumerates the steps we recommend to generate a self-signed
server certificate for a MongoDB instance.

A server certificate is also referred to as a member certificate in the MongoDB
documentation.

We currently use
`easy-rsa version 3
<https://community.openvpn.net/openvpn/wiki/EasyRSA3-OpenVPN-Howto>`_, a 
wrapper over complex ``openssl`` commands and helps us achieve this goal
easily. It is available
`here <https://github.com/OpenVPN/easy-rsa/releases>`_ and licensed under GPLv2.


Step 1: Install Dependencies for Server Certificate Generation
--------------------------------------------------------------

The only dependency for easy-rsa v3 is the presence of the ``openssl``
command, which is available from the ``openssl`` package on Ubuntu and other
Debian-based operating systems.

``sudo apt-get install openssl`` should be enough in most cases.


Step 2: Setup the easyrsa Package for Server Certificate Generation
-------------------------------------------------------------------

Download and extract the latest package.

    .. code:: bash
        
        mkdir member-cert && cd member-cert

        wget https://github.com/OpenVPN/easy-rsa/archive/3.0.1.tar.gz

        tar xzvf 3.0.1.tar.gz


This should give you a ``member-cert/easy-rsa-3.0.1`` directory.


Step 3: Customize the Configuration for Server Certificate
----------------------------------------------------------

We customize the CA setup by creating a ``vars`` file based on the existing
``vars.example`` file bundled in the package.

The values for the ``Distinguished Name`` given below (country, province,
city, org, email) are references and can be changed as per your
deployment. Refer to the ``vars.example`` file for detailed variable descriptions.

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


TODO(Krish): Check if the following modifications are required.
Modify the ``extendedKeyUsage = serverAuth`` to ``extendedKeyUsage =
serverAuth,clientAuth`` in the file x509-types/server.

Refer the MongoDB
`documentation <https://docs.mongodb.com/manual/core/security-x.509/>`_ for
more details on this.


Step 4: Create the Server Private Key and CSR
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


Step 5: Sign the Server Certificate
-----------------------------------

The csr file is located in the instance where you ran the above
commands in ``pki/reqs/mdb-instance-0.req``.

You would then need to send this across to the organization which will sign
this request. This will be the self-signed CA that
:ref:`was created earlier <Setup a Self-Signed Certificate Authority>`.


If you are the federation admin, you can import the csr and sign the
certificate using your easyrsa setup:

    .. code:: bash
        
        ./easyrsa import-req mdb-instance-0.req mdb-instance-0

        ./easyrsa --subject-alt-name=DNS:localhost,DNS:mdb-instance-0 sign-req server mdb-instance-0
        
Once you have signed it, you can send the signed certificate and the CA 
certificate back to the requestor.

The files are ``pki/issued/mdb-instance-0.crt`` and ``pki/ca.crt``.


Step 6: Generate the Consolidated Server PEM File
-------------------------------------------------

MongoDB requires a single, consolidated file containing both the public and
private keys.

    .. code:: bash
        
        cat mdb-instance-0.crt mdb-instance-0.key > mdb-instance-0.pem

The only thing left now is to set the ``net.ssl.PEMKeyFile`` parameter to the
path of the ``mdb-instance-0.pem`` file, and the ``net.ssl.CAFile`` parameter
to the ``ca.crt`` file.

