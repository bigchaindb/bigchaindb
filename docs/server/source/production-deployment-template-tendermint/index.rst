Production Deployment Template: Tendermint BFT
==============================================

This section outlines how *we* deploy production BigchainDB,
integrated with Tendermint(backend for BFT consensus),
clusters on Microsoft Azure using
Kubernetes. We improve it constantly.
You may choose to use it as a template or reference for your own deployment,
but *we make no claim that it is suitable for your purposes*.
Feel free change things to suit your needs or preferences.


.. toctree::
   :maxdepth: 1
   
   workflow
   architecture
   node-on-kubernetes
   node-config-map-and-secrets
   bigchaindb-network-on-kubernetes