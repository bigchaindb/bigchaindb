"""A Python 3 script to write a file with a specified number
of keypairs, using bigchaindb.crypto.generate_key_pair()
The file is always named keypairs.py and it should be interpreted
as a Python 3 script.

Usage:
    $ python3 write_keypairs_file.py <num_pairs>

Using the list in other Python scripts:
    from keypairs import keypairs_list
    # keypairs_list is a list of (sk, pk) tuples
    # sk = signing key (private key)
    # pk = verifying key (public key)
"""

import argparse

from bigchaindb import crypto


# Parse the command-line arguments
desc = 'Write a set of keypairs to keypairs.py'
parser = argparse.ArgumentParser(description=desc)
parser.add_argument('num_pairs',
                    help='number of keypairs to write',
                    type=int)
args = parser.parse_args()
num_pairs = int(args.num_pairs)

# Generate and write the keypairs to keypairs.py
print('Writing {} keypairs to keypairs.py...'.format(num_pairs))
with open('keypairs.py', 'w') as f:
    f.write('"""A set of public/private keypairs for use in deploying\n')
    f.write('BigchainDB servers with a predictable set of keys.\n')
    f.write('"""\n\n')
    f.write('keypairs_list = [')
    for pair_num in range(num_pairs):
        keypair = crypto.generate_key_pair()
        spacer = '' if pair_num == 0 else '    '
        f.write("{}('{}',\n     '{}'),\n".format(
                spacer, keypair[0], keypair[1]))
    f.write('    ]\n')

print('Done.')
