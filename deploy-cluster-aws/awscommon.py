# -*- coding: utf-8 -*-
"""Shared AWS-related global constants and functions.
"""

from __future__ import unicode_literals
import os


# Global constants
AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
AWS_REGION = os.environ['AWS_REGION']


def get_naeips(client0):
    """Get a list of (allocated) non-associated elastic IP addresses
       (NAEIPs) on EC2.

    Args:
        client0: A client created from an EC2 resource.
                 e.g. client0 = ec2.meta.client
                 See http://boto3.readthedocs.org/en/latest/guide/clients.html

    Returns:
        A list of NAEIPs in the EC2 account associated with the client.
        To interpret the contents, see http://tinyurl.com/hrnuy74
    """
    # response is a dict with 2 keys: Addresses and ResponseMetadata
    # See http://tinyurl.com/hrnuy74
    response = client0.describe_addresses()
    allocated_eips = response['Addresses']
    non_associated_eips = []
    for eip in allocated_eips:
        if 'InstanceId' not in eip:
            non_associated_eips.append(eip)
    return non_associated_eips
