# Run BigchainDB with Ansible

**NOT for Production Use**

You can use the following instructions to deploy a single or multi node
BigchainDB setup for dev/test using Ansible. Ansible will setup BigchainDB node(s) along with
[Docker](https://www.docker.com/), [Docker Compose](https://docs.docker.com/compose/),
[MongoDB](https://www.mongodb.com/), [BigchainDB Python driver](https://docs.bigchaindb.com/projects/py-driver/en/latest/).

Currently, this workflow is only supported for the following distributions:
- Ubuntu >= 16.04
- CentOS >= 7
- Fedora >= 24

## Minimum Requirements | Ansible
Minimum resource requirements for a single node BigchainDB dev setup. **The more the better**:
- Memory >= 512MB
- VCPUs >= 1
## Clone the BigchainDB repository | Ansible
```text
$ git clone https://github.com/bigchaindb/bigchaindb.git
```

## Install dependencies | Ansible
- [Ansible](http://docs.ansible.com/ansible/latest/intro_installation.html)

You can also install `ansible` and other dependecies, if any, using the `boostrap.sh` script
inside the BigchainDB repository.
Navigate to `bigchaindb/pkg/scripts` and run the `bootstrap.sh` script to install the dependecies
for your OS. The script also checks if the OS you are running is compatible with the
supported versions.

**Note**: `bootstrap.sh` only supports Ubuntu >= 16.04, CentOS >= 7 and Fedora >=24.

```text
$ cd bigchaindb/pkg/scripts/
$ sudo ./bootstrap.sh
```

### BigchainDB Setup Configuration(s) | Ansible
#### Local Setup | Ansible
You can run the Ansible playbook `bdb-deploy.yml` on your local dev machine and set up the BigchainDB node where
BigchainDB can be run as a process or inside a Docker container(s) depending on your configuratin.

Before, running the playbook locally, you need to update the `hosts` and `bdb-config.yml` configuration, which will notify Ansible that we need to run the play locally.

##### Update Hosts | Local
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
##### Update Configuration | Local
Navigate to `bigchaindb/pkg/configuration/vars` inside the BigchainDB repository.
```text
$ cd bigchaindb/pkg/configuration/vars/bdb-config.yml
```

Edit `bdb-config.yml` configuration file as per your requirements, sample configuration file(s):
```text
---
deploy_docker: false #[true, false]
docker_cluster_size: 1 # Only needed if `deploy_docker` is true
bdb_hosts:
  - name: "<HOSTNAME>" # Hostname of dev machine
```
**Note**: You can also orchestrate a multi-node BigchainDB cluster on a local dev host using Docker containers.
Here is a sample `bdb-config.yml`
```text
---
deploy_docker: true #[true, false]
docker_cluster_size: 3
bdb_hosts:
  - name: "<LOCAL_DEV_HOST_HOSTNAME>"
```

#### Remote Setup | Ansible
You can also run the Ansible playbook `bdb-deploy.yml` on remote machine(s) and set up the BigchainDB node where
BigchainDB can be run as a process or inside a Docker container(s) depending on your configuration.

Before, running the playbook on a remote host, you need to update the `hosts` and `bdb-config.yml` configuration, which will notify Ansible that we need to run the play on a remote host.

##### Update Hosts | Remote
Navigate to `bigchaindb/pkg/configuration/hosts` inside the BigchainDB repository.
```text
$ cd bigchaindb/pkg/configuration/hosts
```

Edit `all` configuration file:
```text
# Delete any existing configuration in this file and insert
<Remote_Host_IP/Hostname> ansible_ssh_user=<USERNAME> ansible_sudo_pass=<ROOT_PASSWORD>
```

**Note 1**: You can multiple hosts to `all` configuration file. Root password is needed because ansible
will run some tasks that require root permissions.

**Note 2**: You can also use other methods to get inside the remote machines instead of password based SSH. For other methods
please consult [Ansible Documentation](http://docs.ansible.com/ansible/latest/intro_getting_started.html).

##### Update Configuration | Remote
Navigate to `bigchaindb/pkg/configuration/vars` inside the BigchainDB repository.
```text
$ cd bigchaindb/pkg/configuration/vars/bdb-config.yml
```

Edit `bdb-config.yml` configuration file as per your requirements, sample configuration file(s):
```text
---
deploy_docker: false #[true, false]
docker_cluster_size: 1 # Only needed if `deploy_docker` is true
bdb_hosts:
  - name: "<REMOTE_MACHINE_HOSTNAME>"
```

### BigchainDB Setup | Ansible
Now, You can safely run the `bdb-deploy.yml` playbook and everything will be taken care of by `Ansible`. To run the playbook please navigate to the `bigchaindb/pkg/configuration` directory inside the BigchainDB repository and run the `bdb-deploy.yml` playbook.

```text
$ cd bigchaindb/pkg/configuration/

$ sudo ansible-playbook bdb-deploy.yml -i hosts/all
```

After successfull execution of the playbook, you can verify that BigchainDB docker(s)/process(es) is(are) running.

Verify BigchainDB process(es):
```text
$ ps -ef | grep bigchaindb
```

OR

Verify BigchainDB Docker(s):
```text
$ docker ps | grep bigchaindb
```

The playbook also installs the BigchainDB Python Driver,
so you can use it to make transactions
and verify the functionality of your BigchainDB node.
See the [BigchainDB Python Driver documentation](https://docs.bigchaindb.com/projects/py-driver/en/latest/index.html)
for details on how to use it.


Note 1: The `bdb_root_url` can be be one of the following:
```text
# BigchainDB is running as a process
bdb_root_url = http://<HOST-IP>:9984

OR

# BigchainDB is running inside a docker container
bdb_root_url = http://<HOST-IP>:<DOCKER-PUBLISHED-PORT>
```

Note 2: BigchainDB has [other drivers as well](../drivers-clients/index.html).
