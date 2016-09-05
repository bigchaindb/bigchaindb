# -*- coding: utf-8 -*-
"""This script:
0. allocates more elastic IP addresses if necessary,
1. launches the specified number of nodes (instances) on Amazon EC2,
2. tags them with the specified tag,
3. waits until those instances exist and are running,
4. for each instance, it associates an elastic IP address
   with that instance,
5. writes the shellscript add2known_hosts.sh
6. (over)writes a file named hostlist.py
   containing a list of all public DNS names.
7. (over)writes a file named ssh_key.py
   containing the location of the private SSH key file.
"""

from __future__ import unicode_literals
from os.path import expanduser
import sys
import time
import socket
import argparse
import importlib
import botocore
import boto3

from awscommon import get_naeips


SETTINGS = ['NUM_NODES', 'BRANCH', 'WHAT_TO_DEPLOY', 'SSH_KEY_NAME',
            'USE_KEYPAIRS_FILE', 'IMAGE_ID', 'INSTANCE_TYPE', 'SECURITY_GROUP',
            'USING_EBS', 'EBS_VOLUME_SIZE', 'EBS_OPTIMIZED']


class SettingsTypeError(TypeError):
    pass


# Ensure they're using Python 2.5-2.7
pyver = sys.version_info
major = pyver[0]
minor = pyver[1]
print('You are in an environment where "python" is Python {}.{}'.
      format(major, minor))
if not ((major == 2) and (minor >= 5) and (minor <= 7)):
    print('but Fabric only works with Python 2.5-2.7')
    sys.exit(1)

# Parse the command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument("--tag",
                    help="tag to add to all launched instances on AWS",
                    required=True)
parser.add_argument("--deploy-conf-file",
                    help="AWS deployment configuration file",
                    required=True)
args = parser.parse_args()
tag = args.tag
deploy_conf_file = args.deploy_conf_file

# Import all the variables set in the AWS deployment configuration file
# (Remove the '.py' from the end of deploy_conf_file.)
cf = importlib.import_module(deploy_conf_file[:-3])

dir_cf = dir(cf)  # = a list of the attributes of cf
for setting in SETTINGS:
    if setting not in dir_cf:
        sys.exit('{} was not set '.format(setting) +
                 'in the specified AWS deployment '
                 'configuration file {}'.format(deploy_conf_file))
    exec('{0} = cf.{0}'.format(setting))

# Validate the variables set in the AWS deployment configuration file
if not isinstance(NUM_NODES, int):
    raise SettingsTypeError('NUM_NODES should be an int')

if not isinstance(BRANCH, str):
    raise SettingsTypeError('BRANCH should be a string')

if not isinstance(WHAT_TO_DEPLOY, str):
    raise SettingsTypeError('WHAT_TO_DEPLOY should be a string')

if not isinstance(SSH_KEY_NAME, str):
    raise SettingsTypeError('SSH_KEY_NAME should be a string')

if not isinstance(USE_KEYPAIRS_FILE, bool):
    msg = 'USE_KEYPAIRS_FILE should be a boolean (True or False)'
    raise SettingsTypeError(msg)

if not isinstance(IMAGE_ID, str):
    raise SettingsTypeError('IMAGE_ID should be a string')

if not isinstance(INSTANCE_TYPE, str):
    raise SettingsTypeError('INSTANCE_TYPE should be a string')

if not isinstance(SECURITY_GROUP, str):
    raise SettingsTypeError('SECURITY_GROUP should be a string')

if not isinstance(USING_EBS, bool):
    raise SettingsTypeError('USING_EBS should be a boolean (True or False)')

if not isinstance(EBS_VOLUME_SIZE, int):
    raise SettingsTypeError('EBS_VOLUME_SIZE should be an int')

if not isinstance(EBS_OPTIMIZED, bool):
    raise SettingsTypeError('EBS_OPTIMIZED should be a boolean (True or False)')

if NUM_NODES > 64:
    raise ValueError('NUM_NODES should be less than or equal to 64. '
                     'The AWS deployment configuration file sets it to {}'.
                     format(NUM_NODES))

if WHAT_TO_DEPLOY not in ['servers', 'clients']:
    raise ValueError('WHAT_TO_DEPLOY should be either "servers" or "clients". '
                     'The AWS deployment configuration file sets it to {}'.
                     format(WHAT_TO_DEPLOY))

if SSH_KEY_NAME in ['not-set-yet', '', None]:
    raise ValueError('SSH_KEY_NAME should be set. '
                     'The AWS deployment configuration file sets it to {}'.
                     format(SSH_KEY_NAME))

# Since we assume 'gp2' volumes (for now), the possible range is 1 to 16384
if EBS_VOLUME_SIZE > 16384:
    raise ValueError('EBS_VOLUME_SIZE should be <= 16384. '
                     'The AWS deployment configuration file sets it to {}'.
                     format(EBS_VOLUME_SIZE))

# Get an AWS EC2 "resource"
# See http://boto3.readthedocs.org/en/latest/guide/resources.html
ec2 = boto3.resource(service_name='ec2')

# Create a client from the EC2 resource
# See http://boto3.readthedocs.org/en/latest/guide/clients.html
client = ec2.meta.client

# Ensure they don't already have some instances with the specified tag
# Get a list of all instances with the specified tag.
# (Technically, instances_with_tag is an ec2.instancesCollection.)
filters = [{'Name': 'tag:Name', 'Values': [tag]}]
instances_with_tag = ec2.instances.filter(Filters=filters)
# len() doesn't work on instances_with_tag. This does:
num_ins = 0
for instance in instances_with_tag:
    num_ins += 1
if num_ins != 0:
    print('You already have {} instances with the tag {} on EC2.'.
          format(num_ins, tag))
    print('You should either pick a different tag or '
          'terminate all those instances and '
          'wait until they vanish from your EC2 Console.')
    sys.exit(1)

# Before launching any instances, make sure they have sufficient
# allocated-but-unassociated EC2 elastic IP addresses
print('Checking if you have enough allocated-but-unassociated ' +
      'EC2 elastic IP addresses...')

non_associated_eips = get_naeips(client)

print('You have {} allocated elastic IPs which are '
      'not already associated with instances'.
      format(len(non_associated_eips)))

if NUM_NODES > len(non_associated_eips):
    num_eips_to_allocate = NUM_NODES - len(non_associated_eips)
    print('You want to launch {} instances'.
          format(NUM_NODES))
    print('so {} more elastic IPs must be allocated'.
          format(num_eips_to_allocate))
    for _ in range(num_eips_to_allocate):
        try:
            # Allocate an elastic IP address
            # response is a dict. See http://tinyurl.com/z2n7u9k
            response = client.allocate_address(DryRun=False, Domain='standard')
        except botocore.exceptions.ClientError:
            print('Something went wrong when allocating an '
                  'EC2 elastic IP address on EC2. '
                  'Maybe you are already at the maximum number allowed '
                  'by your AWS account? More details:')
            raise
        except:
            print('Unexpected error:')
            raise

print('Commencing launch of {} instances on Amazon EC2...'.
      format(NUM_NODES))

sg_list = [SECURITY_GROUP]

for _ in range(NUM_NODES):
    # Request the launch of one instance at a time
    # (so list_of_instances should contain only one item)
    # See https://tinyurl.com/hbjewbb
    if USING_EBS:
        dm = {
            'DeviceName': '/dev/sdp',
            # Why /dev/sdp? See https://tinyurl.com/z2zqm6n
            'Ebs': {
                'VolumeSize': EBS_VOLUME_SIZE,  # GiB
                'DeleteOnTermination': False,
                'VolumeType': 'gp2',
                'Encrypted': False
            },
            # 'NoDevice': 'device'
            # Suppresses the specified device included
            # in the block device mapping of the AMI.
        }
        list_of_instances = ec2.create_instances(
            ImageId=IMAGE_ID,
            MinCount=1,
            MaxCount=1,
            KeyName=SSH_KEY_NAME,
            InstanceType=INSTANCE_TYPE,
            SecurityGroupIds=sg_list,
            BlockDeviceMappings=[dm],
            EbsOptimized=EBS_OPTIMIZED
        )
    else:  # not USING_EBS
        list_of_instances = ec2.create_instances(
            ImageId=IMAGE_ID,
            MinCount=1,
            MaxCount=1,
            KeyName=SSH_KEY_NAME,
            InstanceType=INSTANCE_TYPE,
            SecurityGroupIds=sg_list
        )

    # Tag the just-launched instances (should be just one)
    for instance in list_of_instances:
        time.sleep(5)
        instance.create_tags(Tags=[{'Key': 'Name', 'Value': tag}])

# Get a list of all instances with the specified tag.
# (Technically, instances_with_tag is an ec2.instancesCollection.)
filters = [{'Name': 'tag:Name', 'Values': [tag]}]
instances_with_tag = ec2.instances.filter(Filters=filters)
print('The launched instances will have these ids:'.format(tag))
for instance in instances_with_tag:
    print(instance.id)

print('Waiting until all those instances exist...')
for instance in instances_with_tag:
    instance.wait_until_exists()

print('Waiting until all those instances are running...')
for instance in instances_with_tag:
    instance.wait_until_running()

print('Associating allocated-but-unassociated elastic IPs ' +
      'with the instances...')

# Get a list of elastic IPs which are allocated but
# not associated with any instances.
# There should be enough because we checked earlier and
# allocated more if necessary.
non_associated_eips_2 = get_naeips(client)

for i, instance in enumerate(instances_with_tag):
    print('Grabbing an allocated but non-associated elastic IP...')
    eip = non_associated_eips_2[i]
    public_ip = eip['PublicIp']
    print('The public IP address {}'.format(public_ip))

    # Associate that Elastic IP address with an instance
    response2 = client.associate_address(
        DryRun=False,
        InstanceId=instance.instance_id,
        PublicIp=public_ip
        )
    print('was associated with the instance with id {}'.
          format(instance.instance_id))

# Get a list of the pubic DNS names of the instances_with_tag
public_dns_names = []
for instance in instances_with_tag:
    public_dns_name = getattr(instance, 'public_dns_name', None)
    if public_dns_name is not None:
        public_dns_names.append(public_dns_name)

# Write a shellscript to add remote keys to ~/.ssh/known_hosts
print('Preparing shellscript to add remote keys to known_hosts')
with open('add2known_hosts.sh', 'w') as f:
    f.write('#!/bin/bash\n')
    for public_dns_name in public_dns_names:
        f.write('ssh-keyscan ' + public_dns_name + ' >> ~/.ssh/known_hosts\n')

# Create a file named hostlist.py containing public_dns_names.
# If a hostlist.py already exists, it will be overwritten.
print('Writing hostlist.py')
with open('hostlist.py', 'w') as f:
    f.write('# -*- coding: utf-8 -*-\n')
    f.write('"""A list of the public DNS names of all the nodes in this\n')
    f.write('BigchainDB cluster/federation.\n')
    f.write('"""\n')
    f.write('\n')
    f.write('from __future__ import unicode_literals\n')
    f.write('\n')
    f.write('public_dns_names = {}\n'.format(public_dns_names))

# Create a file named ssh_key.py
# containing the location of the private SSH key file.
# If a ssh_key.py already exists, it will be overwritten.
print('Writing ssh_key.py')
with open('ssh_key.py', 'w') as f:
    f.write('# -*- coding: utf-8 -*-\n')
    f.write('"""This file exists as a convenient way for Fabric to get\n')
    f.write('the location of the private SSH key file.')
    f.write('"""\n')
    f.write('\n')
    f.write('from __future__ import unicode_literals\n')
    f.write('\n')
    home = expanduser('~')
    f.write('ssh_key_path = "{}/.ssh/{}"\n'.format(home, SSH_KEY_NAME))

# For each node in the cluster, check port 22 (ssh) until it's reachable
for instance in instances_with_tag:
    ip_address = instance.public_ip_address
    # Create a socket
    # Address Family: AF_INET (means IPv4)
    # Type: SOCK_STREAM (means connection-oriented TCP protocol)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('Attempting to connect to {} on port 22 (ssh)...'.
          format(ip_address))
    unreachable = True
    while unreachable:
        try:
            # Open a connection to the remote node on port 22
            s.connect((ip_address, 22))
        except socket.error as e:
            print('  Socket error: {}'.format(e))
            print('  Trying again in 3 seconds')
            time.sleep(3.0)
        else:
            print('  Port 22 is reachable!')
            s.shutdown(socket.SHUT_WR)
            s.close()
            unreachable = False
