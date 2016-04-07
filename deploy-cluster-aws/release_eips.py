# -*- coding: utf-8 -*-
"""Release all allocated but non-associated elastic IP addresses
(EIPs). Why? From the AWS docs:

``To ensure efficient use of Elastic IP addresses, we impose a small
hourly charge if an Elastic IP address is not associated with a
running instance, or if it is associated with a stopped instance or
an unattached network interface. While your instance is running,
you are not charged for one Elastic IP address associated with the
instance, but you are charged for any additional Elastic IP
addresses associated with the instance. For more information, see
Amazon EC2 Pricing.''

Source: http://tinyurl.com/ozhxatx
"""

from __future__ import unicode_literals
import botocore
import boto3
from awscommon import get_naeips

# Get an AWS EC2 "resource"
# See http://boto3.readthedocs.org/en/latest/guide/resources.html
ec2 = boto3.resource(service_name='ec2')

# Create a client from the EC2 resource
# See http://boto3.readthedocs.org/en/latest/guide/clients.html
client = ec2.meta.client

non_associated_eips = get_naeips(client)

print('You have {} allocated elactic IPs which are '
      'not associated with instances'.
      format(len(non_associated_eips)))

for i, eip in enumerate(non_associated_eips):
    public_ip = eip['PublicIp']
    print('{}: Releasing {}'.format(i, public_ip))
    domain = eip['Domain']
    print('(It has Domain = {}.)'.format(domain))
    try:
        if domain == 'vpc':
            client.release_address(AllocationId=eip['AllocationId'])
        else:
            client.release_address(PublicIp=public_ip)
    except botocore.exceptions.ClientError as e:
        print('A boto error occurred:')
        raise
    except:
        print('An unexpected error occurred:')
        raise
