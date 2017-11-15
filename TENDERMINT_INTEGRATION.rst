**********************
Tendermint Integration
**********************
Quick reference for developers working on the Tendermint integration in
BigchainDB.

Running a single node with ``docker-compose``
=============================================

.. code-block:: bash

    $ docker-compose -f docker-compose.tendermint.yml up bdb

The above command will launch all 3 main required services/processes:

* ``mongodb``
* ``tendermint``
* ``bigchaindb``

To follow the logs of the ``tendermint`` service:

.. code-block:: bash

    $ docker-compose -f docker-compose.tendermint.yml logs -f tendermint

Simple health check:

.. code-block:: bash

    $ docker-compose -f docker-compose.tendermint.yml up curl-client

Post and retrieve a transaction -- copy/paste a driver basic example of a
``CREATE`` transaction:

.. code-block:: bash

    $ docker-compose -f docker-compose.tendermint.yml run --rm driver ipython

.. todo:: small python script to post and retrieve a transaction.


Running a 4-node cluster with ``docker-compose``
================================================


.. code-block:: bash

    $ docker-compose -f docker-compose.network.yml up -d bdb-one bdb-two bdb-three bdb-four


Simple health check:

.. code-block:: bash

    $ docker-compose -f docker-compose.network.yml up curl-client
