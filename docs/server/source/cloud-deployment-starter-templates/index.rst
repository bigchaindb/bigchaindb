Cloud Deployment Starter Templates
==================================

We have some "starter templates" to deploy a basic, working, but bare-bones BigchainDB node on various cloud providers. They should *not* be used as-is to deploy a node for production. They can be used as a starting point. A full production node should meet the requirements outlined in the section on :doc:`production node assumptions, components and requirements <../nodes/index>`.

You don't have to use the tools we use in the starter templates (e.g. Terraform and Ansible). You can use whatever tools you prefer.

If you find the cloud deployment starter templates for nodes helpful, then you may also be interested in our scripts for :doc:`deploying a testing cluster on AWS <../clusters-feds/aws-testing-cluster>` (documented in the Clusters & Federations section).

.. toctree::
   :maxdepth: 1

   template-terraform-aws
   template-ansible
   template-azure
