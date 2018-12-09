
.. Copyright BigchainDB GmbH and BigchainDB contributors
   SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
   Code is Apache-2.0 and docs are CC-BY-4.0

.. _how-to-install-and-configure-easyrsa:

How to Install & Configure Easy-RSA
===================================

We use
`Easy-RSA version 3
<https://community.openvpn.net/openvpn/wiki/EasyRSA3-OpenVPN-Howto>`_, a 
wrapper over complex ``openssl`` commands.
`Easy-RSA is available on GitHub <https://github.com/OpenVPN/easy-rsa/releases>`_ and licensed under GPLv2.


Step 1: Install Easy-RSA Dependencies
-------------------------------------

The only dependency for Easy-RSA v3 is ``openssl``,
which is available from the ``openssl`` package on Ubuntu and other
Debian-based operating systems, i.e. you can install it using:

.. code:: bash

   sudo apt-get update

   sudo apt-get install openssl


Step 2: Install Easy-RSA
------------------------

Make sure you're in the directory where you want Easy-RSA to live,
then download it and extract it within that directory:

.. code:: bash

   wget https://github.com/OpenVPN/easy-rsa/archive/3.0.1.tar.gz

   tar xzvf 3.0.1.tar.gz

   rm 3.0.1.tar.gz

There should now be a directory named ``easy-rsa-3.0.1``
in your current directory.


Step 3: Customize the Easy-RSA Configuration
--------------------------------------------

We now create a config file named ``vars``
by copying the existing ``vars.example`` file
and then editing it.
You should change the 
country, province, city, org and email
to the correct values for your organisation.
(Note: The country, province, city, org and email are part of
the `Distinguished Name <https://en.wikipedia.org/wiki/X.509#Certificates>`_ (DN).)
The comments in the file explain what each of the variables mean.

.. code:: bash
        
   cd easy-rsa-3.0.1/easyrsa3

   cp vars.example vars

   echo 'set_var EASYRSA_DN "org"' >> vars
   echo 'set_var EASYRSA_KEY_SIZE 4096' >> vars
        
   echo 'set_var EASYRSA_REQ_COUNTRY "DE"' >> vars
   echo 'set_var EASYRSA_REQ_PROVINCE "Berlin"' >> vars
   echo 'set_var EASYRSA_REQ_CITY "Berlin"' >> vars
   echo 'set_var EASYRSA_REQ_ORG "BigchainDB GmbH"' >> vars
   echo 'set_var EASYRSA_REQ_OU "IT"' >> vars
   echo 'set_var EASYRSA_REQ_EMAIL "devs@bigchaindb.com"' >> vars

Note: Later, when building a CA or generating a certificate signing request, you will be prompted to enter a value for the OU (or to accept the default). You should change the default OU from ``IT`` to one of the following, as appropriate:
``ROOT-CA``,
``MongoDB-Instance``, ``BigchainDB-Instance``, ``MongoDB-Mon-Instance`` or
``MongoDB-Backup-Instance``.
To understand why, see `the MongoDB Manual <https://docs.mongodb.com/manual/tutorial/configure-x509-client-authentication/>`_.
There are reminders to do this in the relevant docs.


Step 4: Maybe Edit x509-types/server
------------------------------------

.. warning::

   Only do this step if you are setting up a self-signed CA.

   Edit the file ``x509-types/server`` and change
   ``extendedKeyUsage = serverAuth`` to
   ``extendedKeyUsage = serverAuth,clientAuth``.
   See `the MongoDB documentation about x.509 authentication <https://docs.mongodb.com/manual/core/security-x.509/>`_ to understand why.
