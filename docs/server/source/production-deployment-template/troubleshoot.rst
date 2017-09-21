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
        memory: 3.5G

So, when the MongoDB cache occupies a memory greater than 3.5GB, it is
terminated by the ``kubelet``.
This can usually be verified by logging in to the worker node running MongoDB
container and looking at the syslog (the ``journalctl`` command should usually
work). It should show an error message as:

TODO: paste the error message the next time this error happens!


2. 502 Bad Gateway Error on Runscope Tests
------------------------------------------

It means that NGINX could not find the appropriate backed to forward the
requests to. This typically happens when MongoDB goes down (as described above)
and BigchainDB, after trying for ``BIGCHAINDB_DATABASE_MAXTRIES`` times, gives
up. The Kubernetes BigchainDB Deployment then restarts the BigchainDB pod.


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

This issue is fixed in Kubernetes v1.7.


4. Single Disk Attached to Multiple Mountpoints in a Container
--------------------------------------------------------------

This is currently the issue faced in one of the clusters and being debugged by
the support team at Microsoft.

An issue has been logged `here
<https://github.com/Azure/acs-engine/issues/1364>`_.

This is apparently fixed in Kubernetes v1.7.2 which include a new disk driver,
but is yet to tested by us.


