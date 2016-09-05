# Template: Ansible Playbook to Run a BigchainDB Node on an Ubuntu Machine

If you didn't read the introduction to the [cloud deployment starter templates](index.html), please do that now. The main point is that they're not for deploying a production node; they can be used as a starting point.

This page explains how to use [Ansible](https://www.ansible.com/) to install, configure and run all the software needed to run a one-machine BigchainDB node on a server running Ubuntu 14.04.


## Install Ansible

The Ansible documentation has [installation instructions](https://docs.ansible.com/ansible/intro_installation.html). Note the control machine requirements: at the time of writing, Ansible required Python 2.6 or 2.7. (Support for Python 3 [is a goal of Ansible 2.2](https://github.com/ansible/ansible/issues/15976#issuecomment-221264089).)

For example, you could create a special Python 2.x virtualenv named `ansenv` and then install Ansible in it:
```text
cd repos/bigchaindb/ntools
virtualenv -p /usr/local/lib/python2.7.11/bin/python ansenv
source ansenv/bin/activate
pip install ansible
```

## About Our Example Ansible Playbook 

Our example Ansible playbook installs, configures and runs a basic BigchainDB node on an Ubuntu 14.04 machine. That playbook is in `.../bigchaindb/ntools/one-m/ansible/one-m-node.yml`.

When you run the playbook (as per the instructions below), it ensures all the necessary software is installed, configured and running. It can be used to get a BigchainDB node set up on a bare Ubuntu 14.04 machine, but it can also be used to ensure that everything is okay on a running BigchainDB node. (If you run the playbook against a host where everything is okay, then it won't change anything on that host.)


## Create an Ansible Inventory File

An Ansible "inventory" file is a file which lists all the hosts (machines) you want to manage using Ansible. (Ansible will communicate with them via SSH.) Right now, we only want to manage one host.

First, determine the public IP address of the host (i.e. something like `192.0.2.128`).

Then create a one-line text file named `hosts` by doing this:
```text
# cd to the directory .../bigchaindb/ntools/one-m/ansible
echo "192.0.2.128" > hosts
```

but replace `192.0.2.128` with the IP address of the host.


## Run the Ansible Playbook

The next step is to run the Ansible playbook named `one-m-node.yml`:
```text
# cd to the directory .../bigchaindb/ntools/one-m/ansible
ansible-playbook -i hosts --private-key ~/.ssh/<key-name> one-m-node.yml
```

where `<key-name>` should be replaced by the name of the SSH private key you created earlier (for SSHing to the host machine at your cloud hosting provider).

What did you just do? Running that playbook ensures all the software necessary for a one-machine BigchainDB node is installed, configured, and running properly. You can run that playbook on a regular schedule to ensure that the system stays properly configured. If something is okay, it does nothing; it only takes action when something is not as-desired.


## Some Notes on the One-Machine Node You Just Got Running

* It ensures that the installed version of RethinkDB is `2.3.4~0trusty`. You can change that by changing the installation task.
* It uses a very basic RethinkDB configuration file based on `bigchaindb/ntools/one-m/ansible/roles/rethinkdb/templates/rethinkdb.conf.j2`.
* If you edit the RethinkDB configuration file, then running the Ansible playbook will **not** restart RethinkDB for you. You must do that manually. (You can stop RethinkDB using `sudo /etc/init.d/rethinkdb stop`; run the playbook to get RethinkDB started again. This assumes you're using init.d, which is what the Ansible playbook assumes. If you want to use systemd, you'll have to edit the playbook accordingly, and stop RethinkDB using `sudo systemctl stop rethinkdb@<name_instance>`.)
* It generates and uses a default BigchainDB configuration file, which it stores in `~/.bigchaindb` (the default location).
* If you edit the BigchainDB configuration file, then running the Ansible playbook will **not** restart BigchainDB for you. You must do that manually. (You could stop it using `sudo killall -9 bigchaindb`. Run the playbook to get it started again.)


## Optional: Create an Ansible Config File

The above command (`ansible-playbook -i ...`) is fairly long. You can omit the optional arguments if you put their values in an [Ansible configuration file](https://docs.ansible.com/ansible/intro_configuration.html) (config file) instead. There are many places where you can put a config file, but to make one specifically for the "one-m" case, you should put it in `.../bigchaindb/ntools/one-m/ansible/`. In that directory, create a file named `ansible.cfg` with the following contents:
```text
[defaults]
private_key_file = $HOME/.ssh/<key-name>
inventory = hosts
```

where, as before, `<key-name>` must be replaced.


## Next Steps

You could make changes to the Ansible playbook (and the resources it uses) to make the node more production-worthy. See [the section on production node assumptions, components and requirements](../nodes/index.html).
