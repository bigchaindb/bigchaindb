Log Analytics on Azure
======================

This section documents how to create and configure a Log Analytics workspace on
Azure, for a Kubernetes-based deployment.

The documented approach is based on an integration of Microsoft's Operations
Management Suite (OMS) with a Kubernetes-based Azure Container Service cluster.

The :ref:`oms-k8s-references` contains links to more detailed documentation on
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
that you have the Kubernetes command line ``kubectl`` installed.

Creating a workspace and adding a containers solution
-----------------------------------------------------

.. code-block:: bash

    $ az group deployment create --debug \
        --resource-group rg \
        --name "Microsoft.LogAnalyticsOMS" \
        --template-file log_analytics_oms.json \
        --parameters @log_analytics_oms.parameters.json

An example of a simple tenplate file (``--template-file``):

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
    	    "value": "rg-abc-logs"
    	},
    	"solutionType": {
    	    "value": "Containers"
    	},
        }
    }

Deploying the OMS agent(s)
--------------------------
In order to deploy an OMS agent two important pieces of information are needed:

* workspace id
* workspace key

Obtaining the workspace id:

.. code-block:: bash

    $ az resource show 
        --resource-group rg 
        --resource-type Microsoft.OperationalInsights/workspaces 
        --name rg-abc-logs \
        | grep customerId
    "customerId": "12345678-1234-1234-1234-123456789012",

Obtaining the workspace key:


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


.. code-block:: bash

    $ kubectl create -f oms-daemonset.yaml


Some useful management tasks
----------------------------
List workspaces:

.. code-block:: bash
    
    $ az resource list \
        --resource-group rg \
        --resource-type Microsoft.OperationalInsights/workspaces

List solutions:

.. code-block:: bash

    $ az resource list \
        --resource-group rg \
        --resource-type Microsoft.OperationsManagement/solutions

Deleting the containers solution:

.. code-block:: bash

    $ az group deployment delete --debug \
        --resource-group rg \
        --name Microsoft.ContainersOMS

.. code-block:: bash

    $ az resource delete \
        --resource-group rg \
        --resource-type Microsoft.OperationsManagement/solutions \
        --name "Containers(rglogs)"

Deleting the workspace:

.. code-block:: bash
    
    $ az group deployment delete --debug \
        --resource-group rg \
        --name Microsoft.LogAnalyticsOMS

.. code-block:: bash

    $ az resource delete \
        --resource-group rg \
        --resource-type Microsoft.OperationalInsights/workspaces \
        --name rglogs


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
