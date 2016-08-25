# Overview

A BigchainDB production node has more components and requirements than a dev/test node. Those are outlined in the [BigchainDB Nodes](../nodes/index.html) section.

You can provision and deploy a production node (to meet the requirments) using whatever tools you prefer.

This section documents a template (example), showing how one could use certain tools to provision and deploy a prodution node. Feel free to ignore this section or use it to help you with your preferred tools.

In this section, we use:

* [Terraform](https://www.terraform.io/) to provision infrastructure such as AWS instances, storage and security groups, and
* [Ansible](https://www.ansible.com/) to manage the software and files on that infrastructure (configuration management).

If you notice something that could be done better, let us know (e.g. by creating an issue on GitHub).
