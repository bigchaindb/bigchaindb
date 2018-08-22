
.. Copyright BigchainDB GmbH and BigchainDB contributors
   SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
   Code is Apache-2.0 and docs are CC-BY-4.0

.. _configure-mongodb-cloud-manager-for-monitoring:

Configure MongoDB Cloud Manager for Monitoring
==============================================

This document details the steps required to configure MongoDB Cloud Manager to
enable monitoring of data in a MongoDB Replica Set.


Configure MongoDB Cloud Manager for Monitoring
----------------------------------------------

  * Once the Monitoring Agent is up and running, open
    `MongoDB Cloud Manager <https://cloud.mongodb.com>`_.

  * Click ``Login`` under ``MongoDB Cloud Manager`` and log in to the Cloud
    Manager.

  * Select the group from the dropdown box on the page.

  * Go to Settings and add a ``Preferred Hostnames`` entry as
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
    
  * If you have authentication enabled, select the option to enable
    authentication and specify the authentication mechanism as per your
    deployment. The default BigchainDB Kubernetes deployment template currently
    supports ``X.509 Client Certificate`` as the authentication mechanism.
    
  * If you have TLS enabled, select the option to enable TLS/SSL for MongoDB
    connections, and click ``Continue``. This should already be selected for
    you in case you selected ``X.509 Client Certificate`` above.

  * Wait a minute or two for the deployment to be found and then
    click the ``Continue`` button again.

  * Verify that you see your process on the Cloud Manager UI.
    It should look something like this:

    .. image:: /_static/mongodb_cloud_manager_1.png
  
  * Click ``Continue``.

  * Verify on the UI that data is being sent by the monitoring agent to the
    Cloud Manager. It may take upto 5 minutes for data to appear on the UI.
