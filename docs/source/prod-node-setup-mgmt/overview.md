# Overview

Deploying and managing a production BigchainDB node is much more involved than working with a dev/test node:

* There are more components in a production node; see [the page about node components](../nodes/node-components.html)
* Production nodes need more security
* Production nodes need monitoring
* Production nodes need maintenance, e.g. software upgrades, scaling

Thankfully, there are tools to help! We use:

* [Terraform](https://www.terraform.io/) to provision infrastructure such as AWS instances, storage and security groups
* [Ansible](https://www.ansible.com/) to manage the software installed on that infrastructure (configuration management)
