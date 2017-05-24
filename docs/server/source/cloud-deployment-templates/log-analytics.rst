Log Analytics on Azure
======================

This section documents how to create and configure a Log Analytics workspace on
Azure, for a Kubernetes-based deployment.
The documented approach is based on an integration of Microsoft's Operations
Management Suite (OMS) with a Kubernetes-based Azure Container Service cluster.

The :ref:`oms-k8s-references` section (below) contains links to more detailed documentation on
Azure, and Kubernetes.

There are three main steps involved:

1. Create a workspace (``LogAnalyticsOMS``).
2. Create a ``ContainersOMS`` solution under the workspace.
3. Deploy the OMS agent(s).

Steps 1 and 2 rely on `Azure Resource Manager templates`_ and can be done with
one template so we'll cover them together. Step 3 relies on a
`Kubernetes DaemonSet`_ and will be covered separately.

Minimum Requirements
--------------------
This document assumes that you have already deployed a Kubernetes cluster, and
that you have the Kubernetes command line interface ``kubectl`` installed.

Creating a Workspace and Adding a Containers Solution
-----------------------------------------------------
For the sake of this document and example, we'll assume an existing resource
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
    	},
        }
    }

Deploy the OMS Agents
---------------------
To deploy an OMS agent, two important pieces of information are needed:

* workspace id
* workspace key

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

Resource Groups > (Your k8s cluster's resource group) > Log analytics (OMS) > (Name of the only item listed) > OMS Workspace > OMS Portal

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


Create an Email Alert
---------------------

Suppose you want to get an email whenever there's a logging message
with the CRITICAL or ERROR logging level from any container.
At the time of writing, it wasn't possible to create email alerts
using the Azure Portal (as far as we could tell),
but it *was* possible using the OMS Portal.
(There are instructions to get to the OMS Portal
in the section titled :ref:`Deploy the OMS Agents` above.)
Once you're in the OMS Portal, click on **Log Search**
and enter the query string:

``Type=ContainerLog (critical OR error)``

If you don't see any query results,
try experimenting with the query string and time range
to convince yourself that it's working.
For query syntax help, see the
`Log Analytics search reference <https://docs.microsoft.com/en-us/azure/log-analytics/log-analytics-search-reference>`_.
If you want to exclude the "404 Not Found" errors,
use the query string
"Type=ContainerLog (critical OR error) NOT(404)".
Once you're satisfied with the query string,
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
