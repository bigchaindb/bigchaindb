<!---
Copyright BigchainDB GmbH and BigchainDB contributors
SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
Code is Apache-2.0 and docs are CC-BY-4.0
--->

## Deploying the BigchainDB Web Proxy on a Kubernetes Cluster


### Configure the Web Proxy

* Fill in the configuration details for the proxy in the
  `nginx-https-web-proxy-conf.yaml` file.

* Use the command below to create the appropriate ConfigMap and Secret:
```
kubectl apply -f nginx-https-web-proxy-conf.yaml
```


### Start the Kubernetes Service for BigchainDB Web Proxy

* Use the command below to start the Kubernetes Service:
```
kubectl apply -f nginx-https-web-proxy-svc.yaml
```

* This will give you a public IP address tied to an Azure LB.

* Map this to an available domain of your choice on the Azure portal (or use
  any other DNS service provider!)


### Start the Kubernetes Deployment for BigchainDB Web Proxy

* Use the command below to start the Kubernetes Deployment:
```
kubectl apply -f nginx-https-web-proxy-dep.yaml
```
