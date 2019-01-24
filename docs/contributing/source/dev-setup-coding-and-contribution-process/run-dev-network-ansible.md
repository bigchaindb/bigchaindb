<!---
Copyright BigchainDB GmbH and BigchainDB contributors
SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
Code is Apache-2.0 and docs are CC-BY-4.0
--->

# Run a BigchainDB network with Ansible

**NOT for Production Use**

You can use the following instructions to deploy a single or multi node
BigchainDB network for dev/test using Ansible. Ansible will configure the BigchainDB node(s).

Currently, this workflow is only supported for the following distributions:
- Ubuntu >= 16.04
- CentOS >= 7
- Fedora >= 24
- MacOSX

## Minimum Requirements
Minimum resource requirements for a single node BigchainDB dev setup. **The more the better**:
- Memory >= 512MB
- VCPUs >= 1

## Clone the BigchainDB repository
```text
$ git clone https://github.com/bigchaindb/bigchaindb.git
```

## Install dependencies
- [Ansible](http://docs.ansible.com/ansible/latest/intro_installation.html)

You can also install `ansible` and other dependencies, if any, using the `boostrap.sh` script
inside the BigchainDB repository.
Navigate to `bigchaindb/pkg/scripts` and run the `bootstrap.sh` script to install the dependencies
for your OS. The script also checks if the OS you are running is compatible with the
supported versions.

**Note**: `bootstrap.sh` only supports Ubuntu >= 16.04, CentOS >= 7 and Fedora >=24 and MacOSX.

```text
$ cd bigchaindb/pkg/scripts/
$ bash bootstrap.sh --operation install
```

### BigchainDB Setup Configuration(s)
#### Local Setup
You can run the Ansible playbook `bigchaindb-start.yml` on your local dev machine and set up the BigchainDB node where
BigchainDB can be run as a process or inside a Docker container(s) depending on your configuration.

Before, running the playbook locally, you need to update the `hosts` and `stack-config.yml` configuration, which will notify Ansible that we need to run the play locally.

##### Update Hosts
Navigate to `bigchaindb/pkg/configuration/hosts` inside the BigchainDB repository.
```text
$ cd bigchaindb/pkg/configuration/hosts
```

Edit `all` configuration file:
```text
# Delete any existing configuration in this file and insert
# Hostname of dev machine
<HOSTNAME> ansible_connection=local
```
##### Update Configuration
Navigate to `bigchaindb/pkg/configuration/vars` inside the BigchainDB repository.
```text
$ cd bigchaindb/pkg/configuration/vars/stack-config.yml
```

Edit `bdb-config.yml` configuration file as per your requirements, sample configuration file(s):
```text
---
stack_type: "docker" 
stack_size: "4"


OR

---
stack_type: "local"
stack_type: "1"
```

### BigchainDB Setup
Now, You can safely run the `bigchaindb-start.yml` playbook and everything will be taken care of by `Ansible`. To run the playbook please navigate to the `bigchaindb/pkg/configuration` directory inside the BigchainDB repository and run the `bigchaindb-start.yml` playbook.

```text
$ cd bigchaindb/pkg/configuration/

$ ansible-playbook bigchaindb-start.yml -i hosts/all --extra-vars "operation=start home_path=$(pwd)"
```

After successful execution of the playbook, you can verify that BigchainDB docker(s)/process(es) is(are) running.

Verify BigchainDB process(es):
```text
$ ps -ef | grep bigchaindb
```

OR

Verify BigchainDB Docker(s):
```text
$ docker ps | grep bigchaindb
```

You can now send transactions and verify the functionality of your BigchainDB node.
See the [BigchainDB Python Driver documentation](https://docs.bigchaindb.com/projects/py-driver/en/latest/index.html)
for details on how to use it.

**Note**: The `bdb_root_url` can be be one of the following:
```text
# BigchainDB is running as a process
bdb_root_url = http://<HOST-IP>:9984

OR

# BigchainDB is running inside a docker container
bdb_root_url = http://<HOST-IP>:<DOCKER-PUBLISHED-PORT>
```

**Note**: BigchainDB has [other drivers as well](http://docs.bigchaindb.com/projects/server/en/latest/drivers-clients/index.html).

### Experimental: Running Ansible a Remote Dev/Host
#### Remote Setup
You can also run the Ansible playbook `bigchaindb-start.yml` on remote machine(s) and set up the BigchainDB node where
BigchainDB can run as a process or inside a Docker container(s) depending on your configuration.

Before, running the playbook on a remote host, you need to update the `hosts` and `stack-config.yml` configuration, which will notify Ansible that we need to run the play on a remote host.

##### Update Hosts
Navigate to `bigchaindb/pkg/configuration/hosts` inside the BigchainDB repository.
```text
$ cd bigchaindb/pkg/configuration/hosts
```

Edit `all` configuration file:
```text
# Delete any existing configuration in this file and insert
<Remote_Host_IP/Hostname> ansible_ssh_user=<USERNAME> ansible_sudo_pass=<PASSWORD>
```

**Note**: You can add multiple hosts to the `all` configuration file. Non-root user with sudo enabled password is needed because ansible will run some tasks that require those permissions.

**Note**: You can also use other methods to get inside the remote machines instead of password based SSH. For other methods
please consult [Ansible Documentation](http://docs.ansible.com/ansible/latest/intro_getting_started.html).

##### Update Configuration
Navigate to `bigchaindb/pkg/configuration/vars` inside the BigchainDB repository.
```text
$ cd bigchaindb/pkg/configuration/vars/stack-config.yml
```

Edit `stack-config.yml` configuration file as per your requirements, sample configuration file(s):
```text
---
stack_type: "docker" 
stack_size: "4"


OR

---
stack_type: "local"
stack_type: "1"
```

After, the configuration of remote hosts, [run the Ansible playbook and verify your deployment](#bigchaindb-setup-ansible).
