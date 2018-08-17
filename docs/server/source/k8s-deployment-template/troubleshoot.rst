
.. Copyright BigchainDB GmbH and BigchainDB contributors
   SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
   Code is Apache-2.0 and docs are CC-BY-4.0

.. _cluster-troubleshooting:

Cluster Troubleshooting
=======================

This page describes some basic issues we have faced while deploying and
operating the cluster.

1. MongoDB Restarts
-------------------

We define the following in the ``mongo-ss.yaml`` file:

.. code:: bash

    resources:
      limits:
        cpu: 200m
        memory: 5G

When the MongoDB cache occupies a memory greater than 5GB, it is
terminated by the ``kubelet``.
This can usually be verified by logging in to the worker node running MongoDB
container and looking at the syslog (the ``journalctl`` command should usually
work).

This issue is resolved in
`PR #1757 <https://github.com/bigchaindb/bigchaindb/pull/1757>`_.

2. 502 Bad Gateway Error on Runscope Tests
------------------------------------------

It means that NGINX could not find the appropriate backed to forward the
requests to. This typically happens when:

#. MongoDB goes down (as described above) and BigchainDB, after trying for
   ``BIGCHAINDB_DATABASE_MAXTRIES`` times, gives up. The Kubernetes BigchainDB
   Deployment then restarts the BigchainDB pod.

#. BigchainDB crashes for some reason. We have seen this happen when updating
   BigchainDB from one version to the next. This usually means the older
   connections to the service gets disconnected; retrying the request one more
   time, forwards the connection to the new instance and succeed.


3. Service Unreachable
----------------------

Communication between Kubernetes Services and Deployments fail in
v1.6.6 and before due to a trivial key lookup error for non-existent services
in the ``kubelet``.
This error can be reproduced by restarting any public facing (that is, services
using the cloud load balancer) Kubernetes services, and watching the
``kube-proxy`` failure in its logs.
The solution to this problem is to restart ``kube-proxy`` on the affected
worker/agent node. Login to the worker node and run:

.. code:: bash

    docker stop `docker ps | grep k8s_kube-proxy | cut -d" " -f1`
    
    docker logs -f `docker ps | grep k8s_kube-proxy | cut -d" " -f1`

`This issue <https://github.com/kubernetes/kubernetes/issues/48705>`_ is
`fixed in Kubernetes v1.7 <https://github.com/kubernetes/kubernetes/commit/41c4e965c353187889f9b86c3e541b775656dc18>`_.


4. Single Disk Attached to Multiple Mountpoints in a Container
--------------------------------------------------------------

This is currently the issue faced in one of the clusters and being debugged by
the support team at Microsoft.

The issue was first seen on August 29, 2017 on the Test Network and has been
logged in the `Azure/acs-engine repo on GitHub <https://github.com/Azure/acs-engine/issues/1364>`_.

This is apparently fixed in Kubernetes v1.7.2 which include a new disk driver,
but is yet to tested by us.


5. MongoDB Monitoring Agent throws a dial error while connecting to MongoDB
---------------------------------------------------------------------------

You might see something similar to this in the MongoDB Monitoring Agent logs:

.. code:: bash

    Failure dialing host without auth. Err: `no reachable servers`
        at monitoring-agent/components/dialing.go:278
        at monitoring-agent/components/dialing.go:116
        at monitoring-agent/components/dialing.go:213
        at src/runtime/asm_amd64.s:2086


The first thing to check is if the networking is set up correctly. You can use
the (maybe using the `toolbox` container).

If everything looks fine, it might be a problem with the ``Preferred
Hostnames`` setting in MongoDB Cloud Manager. If you do need to change the
regular expression, ensure that it is correct and saved properly (maybe try
refreshing the MongoDB Cloud Manager web page to see if the setting sticks).

Once you update the regular expression, you will need to remove the deployment
and add it again for the Monitoring Agent to discover and connect to the
MongoDB instance correctly.

More information about this configuration is provided in
:doc:`this document <cloud-manager>`.

6. Create a Persistent Volume from existing Azure disk storage Resource
---------------------------------------------------------------------------
When deleting a k8s cluster, all dynamically-created PVs are deleted, along with the
underlying Azure storage disks (so those can't be used in a new cluster). resources
are also deleted thus cannot be used in a new cluster. This workflow will preserve
the Azure storage disks while deleting the k8s cluster and re-use the same disks on a new
cluster for MongoDB persistent storage without losing any data.

The template to create two PVs for MongoDB Stateful Set (One for MongoDB data store and
the other for MongoDB config store) is located at ``mongodb/mongo-pv.yaml``.

You need to configure ``diskName`` and ``diskURI`` in ``mongodb/mongo-pv.yaml`` file. You can get
these values by logging into your Azure portal and going to ``Resource Groups`` and click on your
relevant resource group. From the list of resources click on the storage account resource and
click the container (usually named as ``vhds``) that contains storage disk blobs that are available
for PVs. Click on the storage disk file that you wish to use for your PV and you will be able to
see ``NAME`` and ``URL`` parameters which you can use for ``diskName`` and ``diskURI`` values in
your template respectively and run the following command to create PVs:

.. code:: bash

    $ kubectl --context <context-name> apply -f mongodb/mongo-pv.yaml

.. note:: 

   Please make sure the storage disks you are using are not already being used by any
   other PVs. To check the existing PVs in your cluster, run the following command
   to get PVs and Storage disk file mapping.

   .. code:: bash

       $ kubectl --context <context-name> get pv --output yaml
