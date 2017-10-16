# Run BigchainDB with Ansible

**NOT for Production Use**

You can use the following instructions to deploy a BigchainDB node for
dev/test using Ansible. Ansible will setup a BigchainDB node along with
[Docker](https://www.docker.com/), [Docker Compose](https://docs.docker.com/compose/),
[MongoDB](https://www.mongodb.com/), [BigchainDB Python driver](https://docs.bigchaindb.com/projects/py-driver/en/latest/).

Currently, this workflow is only supported for the following distributions:
- Ubuntu >= 16.04
- CentOS >= 7
- Fedora >= 24

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

```text
$ cd bigchaindb/pkg/scripts/
$ sudo ./bootstrap.sh
```

### Local Setup | Ansible
You can safely run the `quickstart` playbook now and everything will be taken care of by `ansible` on your host. `quickstart` playbook only supports deployment on your dev/local host. To run the playbook please navigate to the ansible directory inside the BigchainDB repository and run the `quickstart` playbook.

```text
$ cd bigchaindb/pkg/ansible/

# All the services will be deployed as processes
$ sudo ansible-playbook quickstart.yml -c local

OR

# To deploy all services inside docker containers
$ sudo ansible-playbook quickstart.yml --extra-vars "with_docker=true" -c local
```

After successfull execution of the playbook, you can verify that BigchainDB docker/process is running.

Verify BigchainDB process:
```text
$ ps -ef | grep bigchaindb
```

OR

Verify BigchainDB Docker:
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
