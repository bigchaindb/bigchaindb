# Install Ansible

The Ansible documentation has [installation instructions](https://docs.ansible.com/ansible/intro_installation.html). Note the control machine requirements: at the time of writing, Ansible required Python 2.6 or 2.7. (Support for Python 3 [is a goal of Ansible 2.2](https://github.com/ansible/ansible/issues/15976#issuecomment-221264089).)

For example, you could create a special Python 2.x virtualenv named `ansenv` and then install Ansible in it:
```text
cd repos/bigchaindb/ntools
virtualenv -p /usr/local/lib/python2.7.11/bin/python ansenv
source ansenv/bin/activate
pip install ansible
```
