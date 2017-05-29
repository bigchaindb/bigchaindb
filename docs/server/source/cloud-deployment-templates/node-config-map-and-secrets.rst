Configure the Node
==================

Use the ConfigMap template in ``configuration/config-map.yaml`` file to
configure the node. Update all the values for the keys in the
ConfigMaps ``vars``, ``mdb-fqdn``, ``bdb-public-key``, ``bdb-keyring`` and
``mongodb-whitelist``.


Use the Secret template in ``configuration/secret.yaml`` file to configure
the secrets for this node. Update all the values for the keys in the Secrets
``mdb-agent-api-key``, ``https-certs``, ``bdb-private-key``,
``threescale-credentials`` and ``mdb-certs``.

You might not need all the keys during the deployment.
For example, if you plan to access the BigchainDB API over HTTP, you might
not need the ``https-certs`` Secret.
   

Ensure that all the secrets are base64 encoded values and the unused ones
are set to an empty string.
For example, assuming that the public key chain is named ``cert.pem`` and
private key is ``cert.key``, run the following commands to encode the
certificates into single continuous string that can be embedded in yaml,
and then copy the contents of ``cert.pem.b64`` in the ``cert.pem`` field,
and the contents of ``cert.key.b64`` in the ``cert.key`` field. 
      

.. code:: bash

    cat cert.pem | base64 -w 0 > cert.pem.b64
    
    cat cert.key | base64 -w 0 > cert.key.b64


Create the ConfigMap and Secret using the commands:

.. code:: bash

   kubectl --context k8s-bdb-test-cluster-0 apply -f configuration/config-map.yaml

   kubectl --context k8s-bdb-test-cluster-0 apply -f configuration/secret.yaml


Some of the Node Configuration Options
--------------------------------------

1. ConfigMap vars.mdb-instance-name

  * MongoDB reads the local ``/etc/hosts`` file while bootstrapping a replica
    set to resolve the hostname provided to the ``rs.initiate()`` command.
    It needs to ensure that the replica set is being initialized in the same
    instance where the MongoDB instance is running.
  * We use the value in the ``mdb-instance-name`` field to achieve this.
  * This field will be the DNS name of your MongoDB instance, and Kubernetes
    maps this name to its internal DNS.
  * This field will also be used by other MongoDB instances when forming a
    MongoDB replica set.
  * We use ``mdb-instance-0``, ``mdb-instance-1`` and so on in our
    documentation.

2. ConfigMap bdb-keyring.bdb-keyring

  * This value specifies the public keys of all the nodes in a BigchainDB
    cluster.
  * It is a ':' separated list, similar to the PATH variables in Unix systems.


3. ConfigMap bdb-public-key.bdb-public-key

  * This value specifies the public key of the current BigchainDB node.

