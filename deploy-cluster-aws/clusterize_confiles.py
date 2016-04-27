# -*- coding: utf-8 -*-
"""Given a directory full of default BigchainDB config files,
transform them into config files for a cluster with proper
keyrings, API endpoint values, etc.

Note: This script assumes that there is a file named hostlist.py
containing public_dns_names = a list of the public DNS names of
all the hosts in the cluster.

Usage:
    python clusterize_confiles.py <dir> <number_of_files>
"""

from __future__ import unicode_literals
import os
import json
import argparse

from hostlist import public_dns_names


# Parse the command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument('dir',
                    help='Directory containing the config files')
parser.add_argument('number_of_files',
                    help='Number of config files expected in dir',
                    type=int)
args = parser.parse_args()

conf_dir = args.dir
numfiles_expected = int(args.number_of_files)

# Check if the number of files in conf_dir is what was expected
conf_files = os.listdir(conf_dir)
numfiles = len(conf_files)
if numfiles != numfiles_expected:
    raise ValueError('There are {} files in {} but {} were expected'.
                     format(numfiles, conf_dir, numfiles_expected))

# Make a list containing all the public keys from
# all the config files
pubkeys = []
for filename in conf_files:
    file_path = os.path.join(conf_dir, filename)
    with open(file_path, 'r') as f:
        conf_dict = json.load(f)
        pubkey = conf_dict['keypair']['public']
        pubkeys.append(pubkey)

# Rewrite each config file, one at a time
for i, filename in enumerate(conf_files):
    file_path = os.path.join(conf_dir, filename)
    with open(file_path, 'r') as f:
        conf_dict = json.load(f)
        # The keyring is the list of *all* public keys
        # minus the config file's own public key
        keyring = list(pubkeys)
        keyring.remove(conf_dict['keypair']['public'])
        conf_dict['keyring'] = keyring
        # Allow incoming server traffic from any IP address
        # to port 9984
        conf_dict['server']['bind'] = '0.0.0.0:9984'
        # Set the api_endpoint
        conf_dict['api_endpoint'] = 'http://' + public_dns_names[i] + \
                                    ':9984/api/v1'
    # Delete the config file
    os.remove(file_path)
    # Write new config file with the same filename
    print('Rewriting {}'.format(file_path))
    with open(file_path, 'w') as f2:
        json.dump(conf_dict, f2)
