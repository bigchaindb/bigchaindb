How to Restore Data Backed On MongoDB Cloud Manager
===================================================

This page describes how to restore data backed up on
`MongoDB Cloud Manager <https://cloud.mongodb.com/>`_ by
the backup agent when using a single instance MongoDB replica set.


Prerequisites
-------------

- You can restore to either new hardware or existing hardware. We cover
  restoring data to an existing MongoDB Kubernetes StatefulSet using a
  Kubernetes Persistent Volume Claim below as described
  :doc:`here <node-on-kubernetes>`.

- If the backup and destination database storage engines or settings do not
  match, mongod cannot start once the backup is restored.

- If the backup and destination database do not belong to the same MongoDB
  Cloud Manager group, then the database will start but never initialize
  properly.

- The backup restore file includes a metadata file, restoreInfo.txt. This file
  captures the options the database used when the snapshot was taken. The
  database must be run with the listed options after it has been restored. It
  contains:
  1. Group name
  2.  Replica Set name
  3.  Cluster Id (if applicable)
  4.  Snapshot timestamp (as Timestamp at UTC)
  5.  Last Oplog applied (as a BSON Timestamp at UTC)
  6.  MongoDB version
  7.  Storage engine type
  8.  mongod startup options used on the database when the snapshot was taken


Step 1: Get the Backup/Archived Data from Cloud Manager
-------------------------------------------------------

- Log in to the Cloud Manager.

- Select the Group that you want to restore data from.

- Click Backup. Hover over the Status column, click on the
  ``Restore Or Download`` button.

- Select the appropriate SNAPSHOT, and click Next.
  
.. note::

  We currently do not support restoring data using the ``POINT IN TIME`` and
  ``OPLOG TIMESTAMP`` method.

- Select 'Pull via Secure HTTP'. Select the number of times the link can be
  used to download data in the dropdown box. We select ``Once``.
  Select the link expiration time - the time till the download link is active.
  We usually select ``1 hour``.

- Check for the email from MongoDB.

.. note::

  This can take some time as the Cloud Manager needs to prepare an archive of
  the backed up data.

- Once you receive the email, click on the link to open the
  ``restore jobs page``. Follow the instructions to download the backup data.

.. note::

  You will be shown a link to download the back up archive. You can either
  click on the ``Download`` button to download it using the browser.
  Under rare circumstances, the download is interrupted and errors out; I have
  no idea why.
  An alternative is to copy the download link and use the ``wget`` tool on
  Linux systems to download the data.

Step 2: Copy the archive to the MongoDB Instance
------------------------------------------------

- Once you have the archive, you can copy it to the MongoDB instance running
  on a Kubernetes cluster using something similar to:

.. code:: bash

   $ kubectl --context ctx-1 cp bigchain-rs-XXXX.tar.gz mdb-instance-name:/

  where ``bigchain-rs-XXXX.tar.gz`` is the archive downloaded from Cloud
  Manager, and ``mdb-instance-name`` is the name of your MongoDB instance.

  
Step 3: Prepare the MongoDB Instance for Restore
------------------------------------------------

- Log in to the MongoDB instance using something like:

.. code:: bash
   
   $ kubectl --context ctx-1 exec -it mdb-instance-name bash

- Extract the archive that we have copied to the instance at the proper
  location using:

.. code:: bash
   
   $ mv /bigchain-rs-XXXX.tar.gz /data/db

   $ cd /data/db

   $ tar xzvf bigchain-rs-XXXX.tar.gz


- Rename the directories on the disk, so that MongoDB can find the correct
  data after we restart it.

- The current database will be located in the ``/data/db/main`` directory.
  We simply rename the old directory to ``/data/db/main.BAK`` and rename the
  backup directory ``bigchain-rs-XXXX`` to ``main``.

.. code:: bash

   $ mv main main.BAK
   
   $ mv bigchain-rs-XXXX main

.. note::
   
   Ensure that there are no connections to MongoDB from any client, in our
   case, BigchainDB. This can be done in multiple ways - iptable rules,
   shutting down BigchainDB, stop sending any transactions to BigchainDB, etc.
   The simplest way to do it is to stop the MongoDB Kubernetes Service.
   BigchainDB has a retry mechanism built in, and it will keep trying to
   connect to MongoDB backend repeatedly till it succeeds.

Step 4: Restart the MongoDB Instance
------------------------------------

- This can be achieved using something like:

.. code:: bash
   
   $ kubectl --context ctx-1 delete -f k8s/mongo/mongo-ss.yaml
   
   $ kubectl --context ctx-1 apply -f  k8s/mongo/mongo-ss.yaml

