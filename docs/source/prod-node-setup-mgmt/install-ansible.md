# Set Up Ansible

## Install Ansible

The Ansible documentation has [installation instructions](https://docs.ansible.com/ansible/intro_installation.html). Note the control machine requirements. At the time of writing, the control machine had to have Python 2.6 or 2.7. (Support for Python 3 [is a goal of Ansible 2.2](https://github.com/ansible/ansible/issues/15976#issuecomment-221264089).) You can ensure you're using a supported version of Python by creating a special Python 2.x virtualenv and installing Ansible in it. For example:
```text
cd repos/bigchaindb/ntools
virtualenv -p /usr/local/lib/python2.7.11/bin/python ansenv
source ansenv/bin/activate
pip install ansible
```


## Create an Ansible Inventory File

An Ansible "inventory" file is a file which lists all the hosts (machines) you want to manage using Ansible. (Ansible will communicate with them via SSH.) Ansible expects the inventory file to be `/etc/ansible/hosts` by default (but you can change that). Here's an example Ansible inventory file for a one-machine BigchainDB node:
```text
node1 ansible_host=192.0.2.128
```

`node1` is a "host alias" (i.e. a made-up name) that you can use when referring to that host in Ansible.
`192.0.2.128` is an example IP address (IPv4): the public IP address of the node.


