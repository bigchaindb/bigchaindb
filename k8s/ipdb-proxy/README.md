## Deploying the IPDB Proxy on a Kubernetes Cluster

### Start the Kubernetes Service for IPDB Proxy

* Use the command below to start the Kubernetes Service:
```
kubectl apply -f ipdb-proxy-svc.yaml
```

* This will give you a public IP address tied to an Azure LB.

* Map this to an available domain of your choice on the Azure portal. I
  typically use something like
  `bigchaindb-getting-started.westeurope.cloudapp.azure.com` to keep it
  simple.

### Start the Kubernetes Deployment for IPDB Proxy

* Use the command below to start the Kubernetes Deployment:
```
kubectl apply -f ipdb-proxy-dep.yaml
```

### Change the Getting Started page to point to this Service

* Change the frontend `Getting Started` page on BigchainDB website to point to
  this new URL
