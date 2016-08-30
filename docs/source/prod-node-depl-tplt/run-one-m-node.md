# Run a One-Machine Node

We have an example Ansible playbook to install, configure and run a basic BigchainDB node on Ubuntu 14.04. It's in `.../bigchaindb/ntools/one-m/ansible/one-m-node.yml`.

When you run the playbook (as per the instructions below), it ensures all the necessary software is installed, configured and running. It can be used to get a BigchainDB node set up on a bare Ubuntu 14.04 machine, but it can also be used to ensure that everything is okay on a running BigchainDB node. (If you run the playbook against a host where everything is okay, then it won't change anything on that host.)

This page explains how to use our example Ansible playbook.


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
* If you edit the RethinkDB configuration file, then running the Ansible playbook will **not** restart RethinkDB for you. You must do that manually. (You could just stop it using `sudo killall -9 rethinkdb` and then run the playbook to get it started again.)
* It generates and uses a default BigchainDB configuration file, which is stores in `~/.bigchaindb` (the default location).
* If you edit the BigchainDB configuration file, then running the Ansible playbook will **not* restart BigchainDB for you. You must do that manually. (You could just stop it using `sudo killall -9 bigchaindb` and then run the playbook to get it started again.)


## Optional: Create an Ansible Config File

The above command (`ansible-playbook -i ...`) is fairly long. You can omit the optional arguments if you put their values in an [Ansible configuration file](https://docs.ansible.com/ansible/intro_configuration.html) (config file) instead. There are many places where you can put a config file, but to make one specifically for the "one-m" case, you should put it in `.../bigchaindb/ntools/one-m/ansible/`. In that directory, create a file named `ansible.cfg` with the following contents:
```text
[defaults]
private_key_file = $HOME/.ssh/<key-name>
inventory = hosts
```

where, as before, `<key-name>` must be replaced.
