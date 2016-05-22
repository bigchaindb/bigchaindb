# -*- coding: utf-8 -*-
"""Given a directory full of default BigchainDB config files,
transform them into config files for a cluster with proper
keyrings, API endpoint values, etc. This script is meant to
be interpreted as a Python 2 script.

Note 1: This script assumes that there is a file named hostlist.py
containing public_dns_names = a list of the public DNS names of
all the hosts in the cluster.

Note 2: If the optional -k argument is included, then a keypairs.py
file must exist and must have enough keypairs in it to assign one
to each of the config files in the directory of config files.
You can create a keypairs.py file using write_keypairs_file.py

Usage:
    python clusterize_confiles.py [-h] [-k] dir number_of_files
"""

from __future__ import unicode_literals

import os
import json
import argparse

from hostlist import public_dns_names

if os.path.isfile('keypairs.py'):
    from keypairs import keypairs_list


# Parse the command-line arguments
desc = 'Transform a directory of default BigchainDB config files '
desc += 'into config files for a cluster'
parser = argparse.ArgumentParser(description=desc)
parser.add_argument('dir',
                    help='Directory containing the config files')
parser.add_argument('number_of_files',
                    help='Number of config files expected in dir',
                    type=int)
parser.add_argument('-k', '--use-keypairs',
                    action='store_true',
                    default=False,
                    help='Use public and private keys from keypairs.py')
args = parser.parse_args()

conf_dir = args.dir
num_files_expected = int(args.number_of_files)
use_keypairs = args.use_keypairs

# Check if the number of files in conf_dir is what was expected
conf_files = sorted(os.listdir(conf_dir))
num_files = len(conf_files)
if num_files != num_files_expected:
    raise ValueError('There are {} files in {} but {} were expected'.
                     format(num_files, conf_dir, num_files_expected))

# If the -k option was included, check to make sure there are enough keypairs
# in keypairs_list
num_keypairs = len(keypairs_list)
if use_keypairs:
    if num_keypairs < num_files:
        raise ValueError('There are {} config files in {} but '
                         'there are only {} keypairs in keypairs.py'.
                         format(num_files, conf_dir, num_keypairs))

# Make a list containing all the public keys
if use_keypairs:
    print('Using keypairs from keypairs.py')
    pubkeys = [keypair[1] for keypair in keypairs_list[:num_files]]
else:
    # read the pubkeys from the config files in conf_dir
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
        # If the -k option was included
        # then replace the private and public keys
        # with those from keypairs_list
        if use_keypairs:
            keypair = keypairs_list[i]
            conf_dict['keypair']['private'] = keypair[0]
            conf_dict['keypair']['public'] = keypair[1]
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
