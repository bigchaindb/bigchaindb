Configure MongoDB Cloud Manager for Monitoring and Backup
=========================================================

This document details the steps required to configure MongoDB Cloud Manager to
enable monitoring and back up of data in a MongoDB Replica Set.


Configure MongoDB Cloud Manager for Monitoring
----------------------------------------------

  * Once the Monitoring Agent is up and running, open
    `MongoDB Cloud Manager <https://cloud.mongodb.com>`_.

  * Click ``Login`` under ``MongoDB Cloud Manager`` and log in to the Cloud
    Manager.

  * Select the group from the dropdown box on the page.

  * Go to Settings, Group Settings and add a ``Preferred Hostnames`` entry as
    a regexp based on the ``mdb-instance-name`` of the nodes in your cluster.
    It may take up to 5 mins till this setting takes effect.
    You may refresh the browser window and verify whether the changes have
    been saved or not.

    For example, for the nodes in a cluster that are named ``mdb-instance-0``,
    ``mdb-instance-1`` and so on, a regex like ``^mdb-instance-[0-9]{1,2}$``
    is recommended.
   
  * Next, click the ``Deployment`` tab, and then the ``Manage Existing``
    button.

  * On the ``Import your deployment for monitoring`` page, enter the hostname
    to be the same as the one set for ``mdb-instance-name`` in the global
    ConfigMap for a node.
    For example, if the ``mdb-instance-name`` is set to ``mdb-instance-0``,
    enter ``mdb-instance-0`` as the value in this field.

  * Enter the port number as ``27017``, with no authentication.
    
  * If you have TLS enabled, select the option to enable TLS/SSL for MongoDB
    connections, and click ``Continue``.

  * Once the deployment is found, click the ``Continue`` button again.
    This may take about a minute or two.

  * Verify that you see your process on the Cloud Manager UI, and click
    ``Continue`` for the third time.

  * Verify on the UI that data is being sent by the monitoring agent to the
    Cloud Manager. It may take upto 5 minutes for data to appear on the UI.


Configure MongoDB Cloud Manager for Backup
------------------------------------------

  * Once the Backup Agent is up and running, open
    `MongoDB Cloud Manager <https://cloud.mongodb.com>`_.
    
  * Click ``Login`` under ``MongoDB Cloud Manager`` and log in to the Cloud
    Manager.

  * Select the group from the dropdown box on the page.

  * Click ``Backup`` tab.
    
  * Hover over the ``Status`` column of your backup and click ``Start``
    to start the backup.

  * Select the replica set on the side pane and check the box to allow TLS/SSL
    connections.

  * Verify the details of your MongoDB instance and click on ``Start``.

  * It may take up to 5 minutes for the backup process to start.
    During this process, the UI will show the status of the backup process.

  * Verify that data is being backed up on the UI.

