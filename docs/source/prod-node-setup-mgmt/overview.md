# Overview

Deploying and managing a production BigchainDB node is much more involved than working with a dev/test node:

* There are more components in a production node; see [the page about node components](../nodes/node-components.html)
* Production nodes need more security
* Production nodes need monitoring
* Production nodes need maintenance, e.g. software upgrades, scaling

Thankfully, there are tools to help!

[Chef](https://www.chef.io/chef/) is a tool to provision machines, install software on those machines, manage the state of those machines, and more. (When we say "machines," we mean bare-metal servers, virtual machines or containers.)
BigchainDB node operators can use Chef (and related tools) to set up and manage the machines associated with their nodes.

A note about terminology: In the world of Chef, a "node" is what we call a machine. In other words, a "BigchainDB node" may contain several "Chef nodes." 

Before you can deploy a production node, you have to know where the machines will be hosted, e.g. AWS, Azure, Cloud Provider X, or your corporate datacenter. You will need an account with that host so that you can provision machines there.

The next step is to provision a machine and install Chef server on it.
