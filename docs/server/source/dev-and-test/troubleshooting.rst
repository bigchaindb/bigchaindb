######################################
Troubelshooting Guide for Contributors
######################################

*****************************************
Generating new SSL Certificates for Tests
*****************************************

These instructions follow `OpenSSL Certificate Authority <https://jamielinux.com/docs/openssl-certificate-authority/index.html>`_.

Create the root pair
====================

Prepare the ``ca`` directory
----------------------------

.. code-block:: bash

    $ mkdir /root/ca

.. code-block:: bash

    $ cd /root/ca
    $ mkdir certs crl newcerts private
    $ chmod 700 private
    $ touch index.txt
    $ echo 1000 > serial

Prepare the ``ca`` configuration file
-------------------------------------
The config file ``/root/ca/openssl.cnf`` should already be there.


Create the root key
-------------------

.. code-block:: bash

    $ cd /root/ca
    $ openssl genrsa -aes256 -out private/ca.key.pem 4096

    # Enter pass phrase for ca.key.pem: secretpassword
    # Verifying - Enter pass phrase for ca.key.pem: secretpassword
 
    $ chmod 400 private/ca.key.pem


Create the root certificate
---------------------------

.. code-block:: bash

    $ cd /root/ca
    $ openssl req -config openssl.cnf \
          -key private/ca.key.pem \
          -new -x509 -days 7300 -sha256 -extensions v3_ca \
          -out certs/ca.cert.pem
    
    # Enter pass phrase for ca.key.pem: secretpassword
    # You are about to be asked to enter information that will be incorporated
    # into your certificate request.
    # -----
    # Country Name (2 letter code) [XX]:GB
    # State or Province Name []:England
    # Locality Name []:
    # Organization Name []:Alice Ltd
    # Organizational Unit Name []:Alice Ltd Certificate Authority
    # Common Name []:Alice Ltd Root CA
    # Email Address []:
    
    $ chmod 444 certs/ca.cert.pem


Verify the root certificate
---------------------------

.. code-block:: bash

    $ openssl x509 -noout -text -in /root/ca/certs/ca.cert.pem


Create the intermediate pair
============================

Prepare the ``ca/intermediate`` directory
-----------------------------------------

.. code-block:: bash

    $ mkdir /root/ca/intermediate
    $ cd /root/ca/intermediate
    $ mkdir certs crl csr newcerts private
    $ chmod 700 private
    $ touch index.txt
    $ echo 1000 > serial
    $ echo 1000 > /root/ca/intermediate/crlnumber

Prepare the ``ca/intermediate`` configuration file
--------------------------------------------------
The config file ``/root/ca/intermediate/openssl.cnf`` should already be there.


Create the intermediate key
---------------------------

.. code-block:: bash

    $ cd /root/ca
    $ openssl genrsa -aes256 \
         -out intermediate/private/intermediate.key.pem 4096
    
    # Enter pass phrase for intermediate.key.pem: secretpassword
    # Verifying - Enter pass phrase for intermediate.key.pem: secretpassword
    
    $ chmod 400 intermediate/private/intermediate.key.pem


Create the intermediate certificate
-----------------------------------

.. warning:: Make sure you specify the intermediate CA configuration
    file (``/root/ca/intermediate/openssl.cnf``).

.. code-block:: bash

    $ cd /root/ca
    $ openssl req -config intermediate/openssl.cnf -new -sha256 \
          -key intermediate/private/intermediate.key.pem \
          -out intermediate/csr/intermediate.csr.pem
    
    # Enter pass phrase for intermediate.key.pem: secretpassword
    # You are about to be asked to enter information that will be incorporated
    # into your certificate request.
    # -----
    # Country Name (2 letter code) [XX]:GB
    # State or Province Name []:England
    # Locality Name []:
    # Organization Name []:Alice Ltd
    # Organizational Unit Name []:Alice Ltd Certificate Authority
    # Common Name []:Alice Ltd Intermediate CA
    # Email Address []:

.. warning:: This time, specify the root CA configuration file
    (``/root/ca/openssl.cnf``).


.. code-block:: bash

    $ cd /root/ca
    $ openssl ca -config openssl.cnf -extensions v3_intermediate_ca \
          -days 3650 -notext -md sha256 \
          -in intermediate/csr/intermediate.csr.pem \
          -out intermediate/certs/intermediate.cert.pem
                  
    Enter pass phrase for ca.key.pem: secretpassword
    Sign the certificate? [y/n]: y
    
    $ chmod 444 intermediate/certs/intermediate.cert.pem

Check index file, it should now contain a line that refers to the intermediate 
certificate.

.. note:: The ``index.txt`` file is where the OpenSSL ``ca`` tool stores
    the certificate database. 

.. warning:: Do not delete or edit this file by hand. 

.. code-block:: bash

    $ cat /root/ca/index.txt
    V       271218225626Z           1000    unknown /C=UV/ST=Cosmicstate/O=Decentralized Nomadic Ants Collective/OU=LeaderLessLab/CN=Intermediate DNACL3/emailAddress=empty@dnac-l3.ion

Verify the intermediate certificate
-----------------------------------

.. code-block:: bash

    $ openssl x509 -noout -text \
          -in intermediate/certs/intermediate.cert.pem

.. code-block:: bash

    $ openssl verify -CAfile certs/ca.cert.pem \
          intermediate/certs/intermediate.cert.pem
    intermediate/certs/intermediate.cert.pem: OK

Create the certificate chain file
---------------------------------

.. code-block:: bash

    $ cat intermediate/certs/intermediate.cert.pem \
         certs/ca.cert.pem > intermediate/certs/ca-chain.cert.pem
    $ chmod 444 intermediate/certs/ca-chain.cert.pem
      
                  


Sign server and client certificates
===================================
Create a key
------------

.. code-block:: bash

    $ cd /root/ca
    $ openssl genrsa -out intermediate/private/merlin.key.pem 2048
    $ chmod 400 intermediate/private/merlin.key.pem




Create a certificate
--------------------

.. code-block:: bash

    $ cd /root/ca
    $ openssl req -config intermediate/openssl.cnf \
          -key intermediate/private/merlin.key.pem \
          -new -sha256 -out intermediate/csr/merlin.csr.pem

    $ Enter pass phrase for merlin.key.pem: secretpassword
    $ You are about to be asked to enter information that will be incorporated
    $ into your certificate request.
    $ -----
    $ Country Name (2 letter code) [XX]:US
    $ State or Province Name []:California
    $ Locality Name []:Mountain View
    $ Organization Name []:Alice Ltd
    $ Organizational Unit Name []:Alice Ltd Web Services
    $ Common Name []: merlin
    $ Email Address []:

.. code-block:: bash

    $ cd /root/ca
    $ openssl ca -config intermediate/openssl.cnf \
          -extensions server_cert -days 375 -notext -md sha256 \
          -in intermediate/csr/merlin.csr.pem \
          -out intermediate/certs/merlin.cert.pem
    $ chmod 444 intermediate/certs/merlin.cert.pem

The ``intermediate/index.txt`` file should contain a line
referring to this new certificate.

.. code-block:: bash

    $ cat /root/ca/intermediate/index.txt

    V       181230234239Z           1000    unknown /C=UV/ST=Cosmicstate/L=zeronest/O=Decentralized Nomadic Ants Collective/OU=LeaderLessLab/CN=merlin-cert/emailAddress=empty@dnac-l3.io


Verify the certificate
----------------------

.. code-block:: bash

    $ openssl x509 -noout -text \
          -in intermediate/certs/merlin.cert.pem

.. note:: The ``Issuer`` is the intermediate CA. The ``Subject`` refers
    to the certificate itself.

.. code-block:: bash

    Signature Algorithm: sha256WithRSAEncryption               
        Issuer: C=UV, ST=Cosmicstate, O=Decentralized Nomadic Ants Collective, OU=LeaderLessLab, CN=Intermediate DNACL3/emailAddress=empty@dnac-l3.ion
        Validity
            Not Before: Dec 20 23:42:39 2017 GMT               
            Not After : Dec 30 23:42:39 2018 GMT
        Subject: C=UV, ST=Cosmicstate, L=zeronest, O=Decentralized Nomadic Ants Collective, OU=LeaderLessLab, CN=merlin-cert/emailAddress=empty@dnac-l3.ion
        Subject Public Key Info:
            Public Key Algorithm: rsaEncryption                
                Public-Key: (2048 bit)                         
                Modulus:       
                    00:cd:a9:27:70:c4:36:73:37:ee:0d:09:27:8e:b6:                                                              



.. code-block:: bash

    $ openssl verify -CAfile intermediate/certs/ca-chain.cert.pem \
          intermediate/certs/merlin.cert.pem

    intermediate/certs/merlin.cert.pem: OK




Deploy the certificate
----------------------
When deploying to a server application (eg, Apache), you 
need to make the following files available:

    * ca-chain.cert.pem
    * merlin.key.pem
    * merlin.cert.pem

Sign client certificate
=======================
Create client key
-----------------

.. code-block:: bash

    $ cd /root/ca
    $ openssl genrsa -out intermediate/private/alice.key.pem 2048
    $ chmod 400 intermediate/private/alice.key.pem




Create client certificate
-------------------------

.. code-block:: bash

    $ cd /root/ca
    $ openssl req -config intermediate/openssl.cnf \
          -key intermediate/private/alice.key.pem \
          -new -sha256 -out intermediate/csr/alice.csr.pem

    $ Enter pass phrase for merlin.key.pem: secretpassword
    $ You are about to be asked to enter information that will be incorporated
    $ into your certificate request.
    $ -----
    $ Country Name (2 letter code) [XX]:US
    $ State or Province Name []:California
    $ Locality Name []:Mountain View
    $ Organization Name []:Alice Ltd
    $ Organizational Unit Name []:Alice Ltd Web Services
    $ Common Name []: merlin
    $ Email Address []:

.. code-block:: bash

    $ cd /root/ca
    $ openssl ca -config intermediate/openssl.cnf \
          -extensions usr_cert -days 375 -notext -md sha256 \
          -in intermediate/csr/alice.csr.pem \
          -out intermediate/certs/alice.cert.pem
    $ chmod 444 intermediate/certs/alice.cert.pem

The ``intermediate/index.txt`` file should contain a line
referring to this new certificate.

.. code-block:: bash

    $ cat /root/ca/intermediate/index.txt

    V       181230234239Z           1000    unknown /C=UV/ST=Cosmicstate/L=zeronest/O=Decentralized Nomadic Ants Collective/OU=LeaderLessLab/CN=merlin-cert/emailAddress=empty@dnac-l3.ion
    V       181231005408Z           1001    unknown /C=UV/ST=Cosmicstate/L=zeronest/O=Decentralized Nomadic Ants Collective/OU=LeaderLessLab/CN=alice/emailAddress=alice@there.xyz




Verify the client certificate
-----------------------------

.. code-block:: bash

    $ openssl x509 -noout -text \
          -in intermediate/certs/alice.cert.pem

.. note:: The ``Issuer`` is the intermediate CA. The ``Subject`` refers
    to the certificate itself.

.. code-block:: bash

    Signature Algorithm: sha256WithRSAEncryption
        Issuer: C=UV, ST=Cosmicstate, O=Decentralized Nomadic Ants Collective, OU=LeaderLessLab, CN=Intermediate DNACL3/emailAddress=empty@dnac-l3.ion
        Validity
            Not Before: Dec 21 00:54:08 2017 GMT
            Not After : Dec 31 00:54:08 2018 GMT
        Subject: C=UV, ST=Cosmicstate, L=zeronest, O=Decentralized Nomadic Ants Collective, OU=LeaderLessLab, CN=alice/emailAddress=alice@there.xyz
        Subject Public Key Info:
            Public Key Algorithm: rsaEncryption
                Public-Key: (2048 bit)
                Modulus:
                    00:d7:e5:30:d6:5f:75:be:72:c9:29:de:67:16:28:



.. code-block:: bash

    $ openssl verify -CAfile intermediate/certs/ca-chain.cert.pem \
          intermediate/certs/alice.cert.pem

    intermediate/certs/alice.cert.pem: OK




Deploy the client certificate
-----------------------------
When deploying to a client application (eg, BigchainDB), you 
need to make the following files available:

    * ca-chain.cert.pem
    * alice.key.pem
    * alice.cert.pem



Certificate revocation lists
============================

Prepare the ``crl`` configuration file
--------------------------------------

When a certificate authority signs a certificate, it will normally encode the CRL location into the certificate. Add crlDistributionPoints to the appropriate sections. In our case, add it to the [ server_cert ] section.

.. code-block:: ini

    [ server_cert ]
    # ... snipped ...
    crlDistributionPoints = URI:http://example.com/intermediate.crl.pem



Create the CRL
--------------

.. code-block:: bash

    $ openssl ca -config intermediate/openssl.cnf \
        -gencrl -out intermediate/crl/intermediate.crl.pem

You can check the contents of the CRL with the crl tool.

.. code-block:: bash

    $ openssl crl -in intermediate/crl/intermediate.crl.pem -noout -text

No certificates have been revoked yet, so the output will state:

.. code-block:: bash

    No Revoked Certificates.

You should re-create the CRL at regular intervals. By default, the
CRL expires after 30 days. This is controlled by the
``default_crl_days`` option in the ``[ CA_default ]`` section.



Revoke a certificate
--------------------
Server-side use of the CRL
--------------------------
Client-side use of the CRL
--------------------------


