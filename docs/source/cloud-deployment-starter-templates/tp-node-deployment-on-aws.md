# Template: Node Deployment on AWS

If you didn't read the introduction to the [cloud deployment starter templates](index.html), please do that now. The main point is that they're not for deploying a production node; they can be used as a starting point.

The template documented on this page uses:

* [Terraform](https://www.terraform.io/) to provision infrastructure resources on AWS, and
* [Ansible](https://www.ansible.com/) to manage the software and files on that infrastructure (configuration management).


## Install Terraform

The [Terraform documentation has installation instructions](https://www.terraform.io/intro/getting-started/install.html) for all common operating systems.

If you don't want to run Terraform on your local machine, you can install it on a cloud machine under your control (e.g. on AWS).

Note: Hashicorp has an enterprise version of Terraform called "Terraform Enterprise." You can license it by itself or get it as part of Atlas. If you decide to license Terraform Enterprise or Atlas, be sure to install it on your own hosting (i.e. "on premise"), not on the hosting provided by Hashicorp. The reason is that BigchainDB clusters are supposed to be decentralized. If everyone used Hashicorp's hosted Atlas, then that would be a point of centralization.

**Ubuntu Installation Tips**

If you want to install Terraform on Ubuntu, first [download the .zip file](https://www.terraform.io/downloads.html). Then install it in `/opt`:
```text
sudo mkdir -p /opt/terraform
sudo unzip path/to/zip-file.zip -d /opt/terraform
```

Why install it in `/opt`? See [the answers at Ask Ubuntu](https://askubuntu.com/questions/1148/what-is-the-best-place-to-install-user-apps).

Next, add `/opt/terraform` to your path. If you use bash for your shell, then you could add this line to `~/.bashrc`:
```text
export PATH="/opt/terraform:$PATH"
```

After doing that, relaunch your shell or force it to read `~/.bashrc` again, e.g. by doing `source ~/.bashrc`. You can verify that terraform is installed and in your path by doing:
```text
terraform --version
```

It should say the current version of Terraform.


## Use Terraform to Provision a One-Machine Node on AWS

We have an example Terraform configuration (set of files) to provision all the resources needed to run a one-machine BigchainDB node on AWS:

* An instance on EC2 (based on an Ubuntu 14.04 AMI)
* A security group
* An EBS volume
* An elastic IP address


## Get Set Up to Use Terraform

First, do the [basic AWS setup steps outlined in the Appendices](../appendices/aws-setup.html).

Then go to the `.../bigchaindb/ntools/one-m/aws/` directory and open the file `variables.tf`. Most of the variables have sensible default values, but you can change them if you like. In particular, you may want to change `aws_region`. (Terraform looks in `~/.aws/credentials` to get your AWS credentials, so you don't have to enter those anywhere.)

The `ssh_key_name` has no default value, so Terraform will prompt you every time it needs it.

To see what Terraform will do, run:
```text
terraform plan
```

It should ask you the value of `ssh_key_name`. 

It figured out the plan by reading all the `.tf` Terraform files in the directory.

If you don't want to be asked for the `ssh_key_name`, you can change the default value of `ssh_key_name` (in the file `variables.tf`) or [you can set an environmen variable](https://www.terraform.io/docs/configuration/variables.html) named `TF_VAR_ssh_key_name`.


## Use Terraform to Provision Resources

To provision all the resources specified in the plan, do the following. **Note: This will provision actual resources on AWS, and those cost money. Be sure to shut down the resources you don't want to keep running later, otherwise the cost will keep growing.**
```text
terraform apply
```

Terraform will report its progress as it provisions all the resources. Once it's done, you can go to the Amazon EC2 web console and see the instance, its security group, its elastic IP, and its attached storage volumes (one for the root directory and one for RethinkDB storage).

At this point, there is no software installed on the instance except for Ubuntu 14.04 and whatever else came with the Amazon Machine Image (AMI) specified in the Terraform configuration (files). The next step is to use Ansible to install, configure and run all the necessary software.


## Optional: "Destroy" the Resources

If you want to shut down all the resources just provisioned, you must first disable termination protection on the instance:

1. Go to the EC2 console and select the instance you just launched. It should be named `BigchainDB_node`.
2. Click **Actions** > **Instance Settings** > **Change Termination Protection** > **Yes, Disable**
3. Back in your terminal, do `terraform destroy`

Terraform should "destroy" (i.e. terminate or delete) all the AWS resources you provisioned above.

If it fails (e.g. because of an attached and mounted EBS volume), then you can terminate the instance using the EC2 console: **Actions** > **Instance State** > **Terminate** > **Yes, Terminate**. Once the instance is terminated, you should still do `terraform destroy` to make sure that all the other resources are destroyed.


## Install Ansible

The Ansible documentation has [installation instructions](https://docs.ansible.com/ansible/intro_installation.html). Note the control machine requirements: at the time of writing, Ansible required Python 2.6 or 2.7. (Support for Python 3 [is a goal of Ansible 2.2](https://github.com/ansible/ansible/issues/15976#issuecomment-221264089).)

For example, you could create a special Python 2.x virtualenv named `ansenv` and then install Ansible in it:
```text
cd repos/bigchaindb/ntools
virtualenv -p /usr/local/lib/python2.7.11/bin/python ansenv
source ansenv/bin/activate
pip install ansible
```

## About Out Example Ansible Playbook 

We have an example Ansible playbook to install, configure and run a basic BigchainDB node on Ubuntu 14.04. It's in `.../bigchaindb/ntools/one-m/ansible/one-m-node.yml`.

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


## Next Steps

You could make changes to the Terraform configuration and the Ansible playbook to make the node more production-worthy. See [the section on production node assumptions, components and requirements](../nodes/index.html).
