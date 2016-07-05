# Example RethinkDB Storage Setups

## Example 1: A Partition of an AWS Instance Store

Many [AWS EC2 instance types](https://aws.amazon.com/ec2/instance-types/) comes with an [instance store](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/InstanceStorage.html): temporary storage that disappears when the instance disappears. The size and setup of an instance store depends on the EC2 instance type.

We have some scripts for [deploying a _test_ BigchainDB cluster on AWS](../clusters-feds/deploy-on-aws.html). Those scripts include commands to set up a partition (`/dev/xvdb`) on an [instance store](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/InstanceStorage.html) for RethinkDB data. Those commands can be found in the file `/deploy-cluster-aws/fabfile.py`, under `def install_rethinkdb()` (i.e. the Fabric function to install RethinkDB).

An AWS instance store is convenient, but it's intended for "buffers, caches, scratch data, and other temporary content." Moreover:

* You pay for all the storage, regardless of how much you use.
* You can't increase the size of the instance store.
* If the instance stops, terminates, or reboots, you lose the associated instance store.
* Instance store data isn't replicated, so if the underlying disk drive fails, you lose the data in the instance store.
* "You can't detach an instance store volume from one instance and attach it to a different instance."

The [AWS documentation says](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/InstanceStorage.html), "...do not rely on instance store for valuable, long-term data. Instead, you can build a degree of redundancy (for example, RAID 1/5/6), or use a file system (for example, HDFS and MapR-FS) that supports redundancy and fault tolerance."

**Even if you don't use an AWS instance store partition to store your node's RethinkDB data, you may find it useful to read the steps in `def install_rethinkdb()`: [see fabfile.py](https://github.com/bigchaindb/bigchaindb/blob/master/deploy-cluster-aws/fabfile.py).**


## Example 2: An Amazon EBS Volume

TODO

Note: Amazon EBS volumes are always replicated.


## Example 3: Using Amazon EFS

TODO


## Other Examples?

TODO

Maybe RAID, ZFS, ... (over EBS volumes, i.e. a DIY Amazon EFS)
