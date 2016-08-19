# Configure a One-Machine Node

In this step, we will install and configure all the software necessary to run BigchainDB, all on one machine.


## Create an Ansible Inventory File

An Ansible "inventory" file is a file which lists all the hosts (machines) you want to manage using Ansible. (Ansible will communicate with them via SSH.) Right now, we only want to manage one host.

First, determine the public IP address of the host (i.e. something like `192.0.2.128`). Below we refer to it as `<ip_address>`.

Create a one-line text file named `hosts` using this command (with `<ip_address>` replaced):
```text
echo "node1 ansible_host=<ip_address>" > hosts
```

`node1` is a "host alias" (i.e. a made-up name) that you can use when referring to that host in Ansible. Move `hosts` to `/etc/ansible/` because that's the default place where Ansible looks for it:
```text
sudo mkdir -p /etc/ansible/
sudo mv hosts /etc/ansible/
```


## Tell Ansible the Location of the SSH Key File

Ansible uses SSH to connect to the remote host, so it needs to know the location of the SSH (private) key file. (The corresponding public key should already be on the host you provisioned earler.) Normally, Ansible will ask for the location of the SSH key file as-needed. You can make it stop asking by putting the location in an [Ansible configuration file](https://docs.ansible.com/ansible/intro_configuration.html) (config file). (If you prefer, you could use [ssh-agent](https://en.wikipedia.org/wiki/Ssh-agent) instead.)

The following command will do that (overwriting any existing file named `ansible.cfg`):
```text
# cd to the .../bigchaindb/ntools/one-m/ansible directory
echo "private_key_file=$HOME/.ssh/<key-name>" > ansible.cfg
```

where `<key-name>` must be replaced by the actual name of the SSH private key file.




