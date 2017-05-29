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

  * Go to Settings, Group Settings and add a Preferred Hostnames regexp as
    ``^mdb-instance-[0-9]{1,2}$``. It may take up to 5 mins till this setting
    is in effect. You may refresh the browser window and verify whether the
    changes have been saved or not.
   
  * Next, click the ``Deployment`` tab, and then the ``Manage Existing``
    button.

  * On the ``Import your deployment for monitoring`` page, enter the hostname
    to be the same as the one set for ``mdb-instance-name`` in the global
    ConfigMap for a node.
    For example, if the ``mdb-instance-name`` is set to ``mdb-instance-0``,
    enter ``mdb-instance-0`` as the value in this field.

  * Enter the port number as ``27017``, with no authentication.
    
  * If you have TLS enabled, select the option to enable TLS/SSL for MongoDB
    connections.

  * Once the deployment is found, click the ``Continue`` button.
    This may take about a minute or two.

  * Do not add ``Automation Agent`` when given an option to add it.

  * Verify on the UI that data is being sent by the monitoring agent to the
    Cloud Manager.


Configure MongoDB Cloud Manager for Backup
------------------------------------------

  * Once the Backup Agent is up and running, open
    `MongoDB Cloud Manager <https://cloud.mongodb.com>`_.
    
  * Click ``Login`` under ``MongoDB Cloud Manager`` and log in to the Cloud
    Manager.

  * Select the group from the dropdown box on the page.

  * Click ``Backup`` tab.
    
  * Click on the ``Begin Setup``.

  * Click on ``Next``, select the replica set from the dropdown menu.

  * Verify the details of your MongoDB instance and click on ``Start`` again.

  * It might take up to 5 minutes to start the backup process.

  * Verify that data is being backed up on the UI.
