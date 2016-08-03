# Example RethinkDB Storage Setups

## Example Amazon EC2 Setups

We have some scripts for [deploying a _test_ BigchainDB cluster on AWS](../clusters-feds/deploy-on-aws.html). Those scripts include command sequences to set up storage for RethinkDB.
In particular, look in the file [/deploy-cluster-aws/fabfile.py](https://github.com/bigchaindb/bigchaindb/blob/master/deploy-cluster-aws/fabfile.py), under `def prep_rethinkdb_storage(USING_EBS)`. Note that there are two cases:

1. **Using EBS ([Amazon Elastic Block Store](https://aws.amazon.com/ebs/)).** This is always an option, and for some instance types ("EBS-only"), it's the only option.
2. **Using an "instance store" volume provided with an Amazon EC2 instance.** Note that our scripts only use one of the (possibly many) volumes in the instance store.

There's some explanation of the steps in the [Amazon EC2 documentation about making an Amazon EBS volume available for use](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ebs-using-volumes.html).

You shouldn't use an EC2 "instance store" to store RethinkDB data for a production node, because it's not replicated and it's only intended for temporary, ephemeral data. If the associated instance crashes, is stopped, or is terminated, the data in the instance store is lost forever. Amazon EBS storage is replicated, has incremental snapshots, and is low-latency.


## Example Using Amazon EFS

TODO


## Other Examples?

TODO

Maybe RAID, ZFS, ... (over EBS volumes, i.e. a DIY Amazon EFS)
