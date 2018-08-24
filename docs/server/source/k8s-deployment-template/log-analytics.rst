
.. Copyright BigchainDB GmbH and BigchainDB contributors
   SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
   Code is Apache-2.0 and docs are CC-BY-4.0

Log Analytics on Azure
======================

This page describes how we use Microsoft Operations Management Suite (OMS)
to collect all logs from a Kubernetes cluster,
to search those logs,
and to set up email alerts based on log messages.
The :ref:`oms-k8s-references` section (below) contains links
to more detailed documentation.

There are two steps:

1. Setup: Create a log analytics OMS workspace
   and a Containers solution under that workspace.
2. Deploy OMS agents to your Kubernetes cluster.


Step 1: Setup
-------------

Step 1 can be done the web browser way or the command-line way.


The Web Browser Way
~~~~~~~~~~~~~~~~~~~

To create a new log analytics OMS workspace:

1. Go to the Azure Portal in your web browser.
2. Click on **More services >** in the lower left corner of the Azure Portal.
3. Type "log analytics" or similar.
4. Select **Log Analytics** from the list of options.
5. Click on **+ Add** to add a new log analytics OMS workspace.
6. Give answers to the questions. You can call the OMS workspace anything,
   but use the same resource group and location as your Kubernetes cluster.
   The free option will suffice, but of course you can also use a paid one.

To add a "Containers solution" to that new workspace:

1. In Azure Portal, in the Log Analytics section, click the name of the new workspace
2. Click **OMS Workspace**.
3. Click **OMS Portal**. It should launch the OMS Portal in a new tab.
4. Click the **Solutions Gallery** tile.
5. Click the **Containers** tile.
6. Click **Add**.


The Command-Line Way
~~~~~~~~~~~~~~~~~~~~

We'll assume your Kubernetes cluster has a resource
group named:

* ``resource_group``

and the workspace we'll create will be named:

* ``work_space``

If you feel creative you may replace these names by more interesting ones.

.. code-block:: bash

    $ az group deployment create --debug \
        --resource-group resource_group \
        --name "Microsoft.LogAnalyticsOMS" \
        --template-file log_analytics_oms.json \
        --parameters @log_analytics_oms.parameters.json

An example of a simple template file (``--template-file``):

.. code-block:: json

    {
      "$schema": "http://schema.management.azure.com/schemas/2014-04-01-preview/deploymentTemplate.json#",
      "contentVersion": "1.0.0.0",
      "parameters": {
        "sku": {
          "type": "String"
        },
        "workspaceName": {
          "type": "String"
        },
        "solutionType": {
          "type": "String"
        },
        "resources": [
          {
            "apiVersion": "2015-03-20",
            "type": "Microsoft.OperationalInsights/workspaces",
            "name": "[parameters('workspaceName')]",
            "location": "[resourceGroup().location]",
            "properties": {
              "sku": {
                "name": "[parameters('sku')]"
              }
            },
            "resources": [
              {
                "apiVersion": "2015-11-01-preview",
                "location": "[resourceGroup().location]",
                "name": "[Concat(parameters('solutionType'), '(', parameters('workspaceName'), ')')]",
                "type": "Microsoft.OperationsManagement/solutions",
                "id": "[Concat(resourceGroup().id, '/providers/Microsoft.OperationsManagement/solutions/', parameters('solutionType'), '(', parameters('workspaceName'), ')')]",
                "dependsOn": [
                  "[concat('Microsoft.OperationalInsights/workspaces/', parameters('workspaceName'))]"
                ],
                "properties": {
                  "workspaceResourceId": "[resourceId('Microsoft.OperationalInsights/workspaces/', parameters('workspaceName'))]"
                },
                "plan": {
                  "publisher": "Microsoft",
                  "product": "[Concat('OMSGallery/', parameters('solutionType'))]",
                  "name": "[Concat(parameters('solutionType'), '(', parameters('workspaceName'), ')')]",
                  "promotionCode": ""
                }
              }
            ]
          }
        ]
      }
    }

An example of the associated parameter file (``--parameters``):

.. code-block:: json
    
    {
      "$schema": "https://schema.management.azure.com/schemas/2015-01-01/deploymentParameters.json#",
      "contentVersion": "1.0.0.0",
      "parameters": {
        "sku": {
          "value": "Free"
        },
        "workspaceName": {
          "value": "work_space"
        },
        "solutionType": {
          "value": "Containers"
        }
      }
    }


Step 2: Deploy the OMS Agents
-----------------------------

To deploy an OMS agent, two important pieces of information are needed:

1. workspace id
2. workspace key

You can obtain the workspace id using:

.. code-block:: bash

    $ az resource show \
        --resource-group resource_group
        --resource-type Microsoft.OperationalInsights/workspaces 
        --name work_space \
        | grep customerId
    "customerId": "12345678-1234-1234-1234-123456789012",

Until we figure out a way to obtain the *workspace key* via the command line,
you can get it via the OMS Portal.
To get to the OMS Portal, go to the Azure Portal and click on:

Resource Groups > (Your Kubernetes cluster's resource group) > Log analytics (OMS) > (Name of the only item listed) > OMS Workspace > OMS Portal

(Let us know if you find a faster way.)
Then see `Microsoft's instructions to obtain your workspace ID and key
<https://docs.microsoft.com/en-us/azure/container-service/container-service-kubernetes-oms#obtain-your-workspace-id-and-key>`_ (via the OMS Portal).

Once you have the workspace id and key, you can include them in the following
YAML file (:download:`oms-daemonset.yaml
<../../../../k8s/logging-and-monitoring/oms-daemonset.yaml>`):

.. code-block:: yaml

    # oms-daemonset.yaml
    apiVersion: extensions/v1beta1
    kind: DaemonSet
    metadata:
      name: omsagent
    spec:
      template:
        metadata:
          labels:
            app: omsagent
        spec:
          containers:
          - env:
            - name: WSID
              value: <workspace_id>
            - name: KEY
              value: <workspace_key>
            image: microsoft/oms
            name: omsagent
            ports:
            - containerPort: 25225
              protocol: TCP
            securityContext:
              privileged: true
            volumeMounts:
            - mountPath: /var/run/docker.sock
              name: docker-sock
          volumes:
          - name: docker-sock
            hostPath:
              path: /var/run/docker.sock

To deploy the OMS agents (one per Kubernetes node, i.e. one per computer),
simply run the following command:

.. code-block:: bash

    $ kubectl create -f oms-daemonset.yaml


Search the OMS Logs
-------------------

OMS should now be getting, storing and indexing all the logs
from all the containers in your Kubernetes cluster.
You can search the OMS logs from the Azure Portal
or the OMS Portal, but at the time of writing,
there was more functionality in the OMS Portal
(e.g. the ability to create an Alert based on a search).

There are instructions to get to the OMS Portal above.
Once you're in the OMS Portal, click on **Log Search**
and enter a query.
Here are some example queries:

All logging messages containing the strings "critical" or "error" (not case-sensitive):

``Type=ContainerLog (critical OR error)``

.. note::

   You can filter the results even more by clicking on things in the left sidebar.
   For OMS Log Search syntax help, see the
   `Log Analytics search reference <https://docs.microsoft.com/en-us/azure/log-analytics/log-analytics-search-reference>`_.

All logging messages containing the string "error" but not "404":

``Type=ContainerLog error NOT(404)``

All logging messages containing the string "critical" but not "CriticalAddonsOnly":

``Type=ContainerLog critical NOT(CriticalAddonsOnly)``

All logging messages from containers running the Docker image bigchaindb/nginx_3scale:1.3, containing the string "GET" but not the strings "Go-http-client" or "runscope" (where those exclusions filter out tests by Kubernetes and Runscope):

``Type=ContainerLog Image="bigchaindb/nginx_3scale:1.3" GET NOT("Go-http-client") NOT(runscope)``

.. note::

   We wrote a small Python 3 script to analyze the logs found by the above NGINX search.
   It's in ``k8s/logging-and-monitoring/analyze.py``. The docsting at the top
   of the script explains how to use it.


Create an Email Alert
---------------------

Once you're satisfied with an OMS Log Search query string,
click the **🔔 Alert** icon in the top menu,
fill in the form,
and click **Save** when you're done.


Some Useful Management Tasks
----------------------------
List workspaces:

.. code-block:: bash
    
    $ az resource list \
        --resource-group resource_group \
        --resource-type Microsoft.OperationalInsights/workspaces

List solutions:

.. code-block:: bash

    $ az resource list \
        --resource-group resource_group \
        --resource-type Microsoft.OperationsManagement/solutions

Delete the containers solution:

.. code-block:: bash

    $ az group deployment delete --debug \
        --resource-group resource_group \
        --name Microsoft.ContainersOMS

.. code-block:: bash

    $ az resource delete \
        --resource-group resource_group \
        --resource-type Microsoft.OperationsManagement/solutions \
        --name "Containers(work_space)"

Delete the workspace:

.. code-block:: bash
    
    $ az group deployment delete --debug \
        --resource-group resource_group \
        --name Microsoft.LogAnalyticsOMS

.. code-block:: bash

    $ az resource delete \
        --resource-group resource_group \
        --resource-type Microsoft.OperationalInsights/workspaces \
        --name work_space


.. _oms-k8s-references:

References
----------

* `Monitor an Azure Container Service cluster with Microsoft Operations Management Suite (OMS) <https://docs.microsoft.com/en-us/azure/container-service/container-service-kubernetes-oms>`_
* `Manage Log Analytics using Azure Resource Manager templates <https://docs.microsoft.com/en-us/azure/log-analytics/log-analytics-template-workspace-configuration>`_
* `azure commands for deployments <https://docs.microsoft.com/en-us/cli/azure/group/deployment>`_
  (``az group deployment``)
* `Understand the structure and syntax of Azure Resource Manager templates <https://docs.microsoft.com/en-us/azure/azure-resource-manager/resource-group-authoring-templates>`_
* `Kubernetes DaemonSet`_



.. _Azure Resource Manager templates: https://docs.microsoft.com/en-us/azure/azure-resource-manager/resource-group-authoring-templates
.. _Kubernetes DaemonSet: https://kubernetes.io/docs/concepts/workloads/controllers/daemonset/
