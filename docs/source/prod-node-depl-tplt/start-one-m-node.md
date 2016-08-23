# Start a One-Machine Node

In this step, we will install, configure and run all the software necessary to run BigchainDB, all on one machine.


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

The next step is to run the Ansible playbook `one-m-node.yml`:
```text
# cd to the directory .../bigchaindb/ntools/one-m/ansible
ansible-playbook -i hosts --private-key ~/.ssh/<key-name> one-m-node.yml
```

where `<key-name>` should be replaced by the name of the SSH private key you created earlier (for SSHing to the host machine at your cloud hosting provider).

What did you just do? Running that playbook ensures all the software necessary for a one-machine BigchainDB node is installed, configured, and running properly. You can run that playbook on a regular schedule to ensure that the system stays properly configured. If something is okay, it does nothing; it only takes action when something is not as-desired.

Note: At the time of writing, the playbook only installs, configures and runs an NTP daemon, but more is coming soon.


## Optional: Create an Ansible Config File

The above command (`ansible-playbook -i ...`) is fairly long. You can omit the optional arguments if you put their values in an [Ansible configuration file](https://docs.ansible.com/ansible/intro_configuration.html) (config file) instead. There are many places where you can put a config file, but to make one specifically for the "one-m" case, you should put it in `.../bigchaindb/ntools/one-m/ansible/`. In that directory, create a file named `ansible.cfg` with the following contents:
```text
[defaults]
private_key_file = $HOME/.ssh/<key-name>
inventory = hosts
```

where, as before, `<key-name>` must be replaced.
