# Overview

Deploying and managing a production BigchainDB node is much more involved than working with a dev/test node:

* There are more components in a production node; see [the page about node components](../nodes/node-components.html)
* Production nodes need more security
* Production nodes need monitoring
* Production nodes need maintenance, e.g. software upgrades, scaling

Thankfully, there are tools that can help (e.g. provisioning tools and configuration management tools). You can use whatever tools you prefer.

As an example, we provide documentation and code showing how to use Terraform and Ansible (together).

* [Terraform](https://www.terraform.io/) to provision infrastructure such as AWS instances, storage and security groups
* [Ansible](https://www.ansible.com/) to manage the software installed on that infrastructure (configuration management)

You can use those as-described or as a reference for setting up your preferred tools. If you notice something that could be done better, let us know (e.g. by creating an issue on GitHub).
