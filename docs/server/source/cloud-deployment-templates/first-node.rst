First Node or Bootstrap Node Setup
==================================

This document is a work in progress and will evolve over time to include 
security, websocket and other settings.


Step 1: Set Up the Cluster
--------------------------

    .. code:: bash

        az group create --name bdb-test-cluster-0 --location westeurope --debug --output json

        ssh-keygen -t rsa -C "k8s-bdb-test-cluster-0" -f ~/.ssh/k8s-bdb-test-cluster-0

        az acs create --name k8s-bdb-test-cluster-0 \
          --resource-group bdb-test-cluster-0 \
          --master-count 3 \
          --agent-count 2 \
          --admin-username ubuntu \
          --agent-vm-size Standard_D2_v2 \
          --dns-prefix k8s-bdb-test-cluster-0 \
          --ssh-key-value ~/.ssh/k8s-bdb-test-cluster-0.pub \
          --orchestrator-type kubernetes \
          --debug --output json

        az acs kubernetes get-credentials \
          --resource-group bdb-test-cluster-0 \
          --name k8s-bdb-test-cluster-0 \
          --debug --output json

        echo -e "Host k8s-bdb-test-cluster-0.westeurope.cloudapp.azure.com\n  ForwardAgent yes" >> ~/.ssh/config


Step 2: Connect to the Cluster UI - (optional)
----------------------------------------------

   * Get the kubectl context for this cluster using ``kubectl config view``.
    
   * For the above commands, the context would be ``k8s-bdb-test-cluster-0``.
    
     .. code:: bash

         kubectl --context k8s-bdb-test-cluster-0 proxy -p 8001

Step 3. Configure the Cluster
-----------------------------

   * Use the ConfigMap in ``configuration/config-map.yaml`` file for configuring
     the cluster.

   * Log in the the MongoDB Cloud Manager and select the group that will monitor
     and backup this cluster from the dropdown box.
     
   * Go to Settings, Group Settings and copy the ``Agent Api Key``.
     
   * Replace the ``<api key here>`` field with this key.

   * Since this is the first node of the cluster, ensure that the ``data.fqdn``
     field has the value ``mdb-instance-0``.

   * We only support the value ``all`` in the ``data.allowed-hosts`` field for now.

   * Create the ConfigMap
    
     .. code:: bash

        kubectl --context k8s-bdb-test-cluster-0 apply -f configuration/config-map.yaml

Step 4. Start the NGINX Service
-------------------------------

   * This will will give us a public IP for the cluster.

   * Once you complete this step, you might need to wait up to 10 mins for the
     public IP to be assigned.

   * You have the option to use vanilla NGINX or an OpenResty NGINX integrated
     with 3scale API Gateway.


Step 4.1. Vanilla NGINX
^^^^^^^^^^^^^^^^^^^^^^^

   *  This configuration is located in the file ``nginx/nginx-svc.yaml``.
    
   *  Since this is the first node, rename ``metadata.name`` and ``metadata.labels.name``
      to ``ngx-instance-0``, and ``spec.selector.app`` to ``ngx-instance-0-dep``.
   
   * Start the Kubernetes Service:
    
      .. code:: bash
      
          kubectl --context k8s-bdb-test-cluster-0 apply -f nginx/nginx-svc.yaml


Step 4.2. OpenResty NGINX + 3scale
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   
   *  You have to enable HTTPS for this one and will need an HTTPS certificate
      for your domain
      
   *  Assuming that the public key chain is named ``cert.pem`` and private key is
      ``cert.key``, run the following commands to encode the certificates into
      single continuous string that can be embedded in yaml.
      
      .. code:: bash

          cat cert.pem | base64 -w 0 > cert.pem.b64
          
          cat cert.key | base64 -w 0 > cert.key.b64

     
   *  Copy the contents of ``cert.pem.b64`` in the ``cert.pem`` field, and the 
      contents of ``cert.key.b64`` in the ``cert.key`` field in the file 
      ``nginx-3scale/nginx-3scale-secret.yaml``
      
   *  Create the Kubernetes Secret:
      
      .. code:: bash

         kubectl --context k8s-bdb-test-cluster-0 apply -f nginx-3scale/nginx-3scale-secret.yaml

   *  Since this is the first node, rename ``metadata.name`` and ``metadata.labels.name``
      to ``ngx-instance-0``, and ``spec.selector.app`` to ``ngx-instance-0-dep`` in
      ``nginx-3scale/nginx-3scale-svc.yaml`` file.
     
   *  Start the Kubernetes Service:
    
      .. code:: bash
 
         kubectl --context k8s-bdb-test-cluster-0 apply -f nginx-3scale/nginx-3scale-svc.yaml


Step 5. Assign DNS Name to the NGINX Public IP
----------------------------------------------

   * The following command can help you find out if the nginx service strated above
     has been assigned a public IP or external IP address:
    
     .. code:: bash
 
         kubectl --context k8s-bdb-test-cluster-0 get svc -w
    
   * Once a public IP is assigned, you can log in to the Azure portal and map it to
     a DNS name.
    
   * We usually start with bdb-test-cluster-0, bdb-test-cluster-1 and so on.
    
   * Let us assume that we assigned the unique name of ``bdb-test-cluster-0`` here.


Step 6. Start the Mongo Kubernetes Service
------------------------------------------

   * Change ``metadata.name`` and ``metadata.labels.name`` to
     ``mdb-instance-0``, and ``spec.selector.app`` to ``mdb-instance-0-ss``.
    
     .. code:: bash
 
         kubectl --context k8s-bdb-test-cluster-0 apply -f mongodb/mongo-svc.yaml


Step 7. Start the BigchainDB Kubernetes Service
-----------------------------------------------

   * Change ``metadata.name`` and ``metadata.labels.name`` to
     ``bdb-instance-0``, and ``spec.selector.app`` to ``bdb-instance-0-dep``.
    
     .. code:: bash
 
         kubectl --context k8s-bdb-test-cluster-0 apply -f bigchaindb/bigchaindb-svc.yaml


Step 8. Start the NGINX Kubernetes Deployment
---------------------------------------------

   * As in step 4, you have the option to use vanilla NGINX or an OpenResty NGINX
     integrated with 3scale API Gateway.

Step 8.1. Vanilla NGINX
^^^^^^^^^^^^^^^^^^^^^^^
   
   * This configuration is located in the file ``nginx/nginx-dep.yaml``.
     
   * Since this is the first node, change the ``metadata.name`` and
     ``spec.template.metadata.labels.app`` to ``ngx-instance-0-dep``.
     
   * Set ``MONGODB_BACKEND_HOST`` env var to
     ``mdb-instance-0.default.svc.cluster.local``.
     
   * Set ``BIGCHAINDB_BACKEND_HOST`` env var to
     ``bdb-instance-0.default.svc.cluster.local``.
     
   * Set ``MONGODB_FRONTEND_PORT`` to
     ``$(NGX_INSTANCE_0_SERVICE_PORT_NGX_PUBLIC_MDB_PORT)``.
     
   * Set ``BIGCHAINDB_FRONTEND_PORT`` to
     ``$(NGX_INSTANCE_0_SERVICE_PORT_NGX_PUBLIC_BDB_PORT)``.
     
     .. code:: bash

         kubectl --context k8s-bdb-test-cluster-0 apply -f nginx/nginx-dep.yaml
   
Step 8.2. OpenResty NGINX + 3scale
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   
   * This configuration is located in the file 
     ``nginx-3scale/nginx-3scale-dep.yaml``.
     
   * Since this is the first node, change the metadata.name and
     spec.template.metadata.labels.app to ``ngx-instance-0-dep``.
     
   * Set ``MONGODB_BACKEND_HOST`` env var to
     ``mdb-instance-0.default.svc.cluster.local``.
     
   * Set ``BIGCHAINDB_BACKEND_HOST`` env var to
     ``bdb-instance-0.default.svc.cluster.local``.
     
   * Set ``MONGODB_FRONTEND_PORT`` to
     ``$(NGX_INSTANCE_0_SERVICE_PORT_NGX_PUBLIC_MDB_PORT)``.
     
   * Set ``BIGCHAINDB_FRONTEND_PORT`` to
     ``$(NGX_INSTANCE_0_SERVICE_PORT_NGX_PUBLIC_BDB_PORT)``.
     
   * Also, replace the placeholder strings for the env vars with the values
     obtained from 3scale. You will need the Secret Token, Service ID, Version Header
     and Provider Key from 3scale.
     
   * The ``THREESCALE_FRONTEND_API_DNS_NAME`` will be DNS name registered for your
     HTTPS certificate.
     
   * You can set the ``THREESCALE_UPSTREAM_API_PORT`` to any port other than 9984,
     9985, 443, 8888 and 27017. We usually use port ``9999``.
     
     .. code:: bash

         kubectl --context k8s-bdb-test-cluster-0 apply -f nginx-3scale/nginx-3scale-dep.yaml


Step 9. Create a Kubernetes Storage Class for MongoDB
-----------------------------------------------------

    .. code:: bash

        kubectl --context k8s-bdb-test-cluster-0 apply -f mongodb/mongo-sc.yaml


Step 10. Create a Kubernetes PersistentVolumeClaim
--------------------------------------------------

    .. code:: bash

        kubectl --context k8s-bdb-test-cluster-0 apply -f mongodb/mongo-pvc.yaml


Step 11. Start a Kubernetes StatefulSet for MongoDB
---------------------------------------------------

   * Change ``spec.serviceName`` to ``mdb-instance-0``.
   
   * Change the ``metadata.name``, ``template.metadata.name`` and
     ``template.metadata.labels.app`` to ``mdb-instance-0-ss``.
    
   * It might take up to 10 minutes for the disks to be created and attached to
     the pod.
    
   * The UI might show that the pod has errored with the
     message "timeout expired waiting for volumes to attach/mount".
    
   * Use the CLI below to check the status of the pod in this case,
     instead of the UI. This happens due to a bug in Azure ACS.
    
     .. code:: bash
     
         kubectl --context k8s-bdb-test-cluster-0 apply -f mongodb/mongo-ss.yaml
    
   * You can check the status of the pod using the command:

     .. code:: bash

        kubectl --context k8s-bdb-test-cluster-0 get po -w


Step 12. Start a Kubernetes Deployment for Bigchaindb
-----------------------------------------------------

   * Change both ``metadata.name`` and ``spec.template.metadata.labels.app``
     to ``bdb-instance-0-dep``.
    
   * Set ``BIGCHAINDB_DATABASE_HOST`` to ``mdb-instance-0``.
    
   * Set the appropriate ``BIGCHAINDB_KEYPAIR_PUBLIC``,
     ``BIGCHAINDB_KEYPAIR_PRIVATE`` values.
    
   * One way to generate BigchainDB keypair is to run a Python shell with
     the command
     ``from bigchaindb_driver import crypto; crypto.generate_keypair()``.
    
     .. code:: bash

         kubectl --context k8s-bdb-test-cluster-0 apply -f bigchaindb/bigchaindb-dep.yaml


Step 13. Start a Kubernetes Deployment for MongoDB Monitoring Agent
-------------------------------------------------------------------

   * Change both metadata.name and spec.template.metadata.labels.app to
     ``mdb-mon-instance-0-dep``.
    
     .. code:: bash

         kubectl --context k8s-bdb-test-cluster-0 apply -f mongodb-monitoring-agent/mongo-mon-dep.yaml

   * Get the pod name and check its logs:

     .. code:: bash

         kubectl --context k8s-bdb-test-cluster-0 get po
         
         kubectl --context k8s-bdb-test-cluster-0 logs -f <pod name>


Step 14. Configure MongoDB Cloud Manager for Monitoring
-------------------------------------------------------

   * Open `MongoDB Cloud Manager <https://cloud.mongodb.com>`_.
   
   * Click ``Login`` under ``MongoDB Cloud Manager`` and log in to the Cloud Manager.
   
   * Select the group from the dropdown box on the page.
   
   * Go to Settings, Group Settings and add a Preferred Hostnames regexp as
     ``^mdb-instance-[0-9]{1,2}$``. It may take up to 5 mins till this setting
     is in effect. You may refresh the browser window and verify whether the changes
     have been saved or not.
   
   * Next, click the ``Deployment`` tab, and then the ``Manage Existing`` button.
   
   * On the ``Import your deployment for monitoring`` page, enter the hostname as
     ``mdb-instance-0``, port number as ``27017``, with no authentication and no 
     TLS/SSL settings.
   
   * Once the deployment is found, click the ``Continue`` button.
     This may take about a minute or two.
   
   * Do not add ``Automation Agent`` when given an option to add it.
   
   * Verify on the UI that data is being by the monitoring agent.


Step 15. Start a Kubernetes Deployment for MongoDB Backup Agent
---------------------------------------------------------------

   * Change both ``metadata.name`` and ``spec.template.metadata.labels.app``
     to ``mdb-backup-instance-0-dep``.
    
     .. code:: bash

         kubectl --context k8s-bdb-test-cluster-0 apply -f mongodb-backup-agent/mongo-backup-dep.yaml

   * Get the pod name and check its logs:

     .. code:: bash

         kubectl --context k8s-bdb-test-cluster-0 get po
         
         kubectl --context k8s-bdb-test-cluster-0 logs -f <pod name>


Step 16. Configure MongoDB Cloud Manager for Backup
---------------------------------------------------

   * Open `MongoDB Cloud Manager <https://cloud.mongodb.com>`_.
     
   * Click ``Login`` under ``MongoDB Cloud Manager`` and log in to the Cloud
     Manager.
     
   * Select the group from the dropdown box on the page.
     
   * Click ``Backup`` tab.
   
   * Click on the ``Begin Setup``.
 
   * Click on ``Next``, select the replica set from the dropdown menu.
   
   * Verify the details of your MongoDB instance and click on ``Start`` again.
   
   * It might take up to 5 minutes to start the backup process.
   
   * Verify that data is being backed up on the UI.


Step 17. Verify that the Cluster is Correctly Set Up
----------------------------------------------------

  * Start the toolbox container in the cluster
  
    .. code:: bash

        kubectl --context k8s-bdb-test-cluster-0 \
          run -it toolbox \
          --image bigchaindb/toolbox \
          --image-pull-policy=Always \
          --restart=Never --rm
    
  * Verify MongoDB instance
    
    .. code:: bash

        nslookup mdb-instance-0
        
        dig +noall +answer _mdb-port._tcp.mdb-instance-0.default.svc.cluster.local SRV
        
        curl -X GET http://mdb-instance-0:27017
    
  * Verify BigchainDB instance
    
    .. code:: bash

        nslookup bdb-instance-0
        
        dig +noall +answer _bdb-port._tcp.bdb-instance-0.default.svc.cluster.local SRV

        dig +noall +answer _bdb-ws-port._tcp.bdb-instance-0.default.svc.cluster.local SRV
        
        curl -X GET http://bdb-instance-0:9984

        wsc ws://bdb-instance-0:9985/api/v1/streams/valid_tx
  
  * Verify NGINX instance
    
    .. code:: bash

        nslookup ngx-instance-0
        
        dig +noall +answer _ngx-public-mdb-port._tcp.ngx-instance-0.default.svc.cluster.local SRV
        
        curl -X GET http://ngx-instance-0:27017 # results in curl: (56) Recv failure: Connection reset by peer
        
        dig +noall +answer _ngx-public-bdb-port._tcp.ngx-instance-0.default.svc.cluster.local SRV

        dig +noall +answer _ngx-public-ws-port._tcp.ngx-instance-0.default.svc.cluster.local SRV
  
  * If you have run the vanilla NGINX instance, run

    .. code:: bash

        curl -X GET http://ngx-instance-0:80

        wsc ws://ngx-instance-0:81/api/v1/streams/valid_tx
  
  * If you have the OpenResty NGINX + 3scale instance, run

    .. code:: bash

        curl -X GET https://ngx-instance-0
  
  * Check the MongoDB monitoring and backup agent on the MongoDB Coud Manager portal to verify they are working fine.
  
  * Send some transactions to BigchainDB and verify it's up and running!

