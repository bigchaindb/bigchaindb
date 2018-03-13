**********************
Tendermint Integration
**********************
Quick reference for developers working on the Tendermint integration in
BigchainDB.

Running a single node with ``docker-compose``
=============================================

.. code-block:: bash

    $ docker-compose up -d bdb

The above command will launch all 3 main required services/processes:

* ``mongodb``
* ``tendermint``
* ``bigchaindb``

To follow the logs of the ``tendermint`` service:

.. code-block:: bash

    $ docker-compose logs -f tendermint

Simple health check:

.. code-block:: bash

    $ docker-compose up curl-client

Post and retrieve a transaction -- copy/paste a driver basic example of a
``CREATE`` transaction:

.. code-block:: bash

    $ docker-compose -f docker-compose.yml run --rm bdb-driver ipython

.. todo:: small python script to post and retrieve a transaction.
