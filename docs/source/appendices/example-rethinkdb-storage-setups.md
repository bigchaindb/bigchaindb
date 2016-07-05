# Example RethinkDB Storage Setups

## Example 1: A Partition of an AWS Instance Store

Many [AWS EC2 instance types](https://aws.amazon.com/ec2/instance-types/) comes with an [instance store](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/InstanceStorage.html): temporary storage that disappears when the instance disappears. (Some instance types _don't_ come with an instance store, but you can attach EBS storage.) The size and setup of an instance store depends on the EC2 instance type.

We have some scripts for [deploying a _test_ BigchainDB cluster on AWS](../clusters-feds/deploy-on-aws.html). Those scripts include commands to set up a partition (`/dev/xvdb`) on the [instance store](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/InstanceStorage.html) if that partition exists. Those commands can be found in the file `/deploy-cluster-aws/fabfile.py`, under `def install_rethinkdb()` (i.e. the function to install RethinkDB).


TODO: Discuss if/when one would use the instance store to store RethinkDB data.



## Example 2: An Amazon EBS Volume

Amazon EBS volumes are always replicated.


## Example 3: Using Amazon EFS

TODO


## Example 4: A RAID Example?

Maybe make two EBS volumes look like one?

