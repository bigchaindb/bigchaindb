# -*- coding: utf-8 -*-
"""This script validates the values in deploy_conf.py
"""

from __future__ import unicode_literals

import sys

from deploy_conf import *

try:
    assert isinstance(NUM_NODES, int)
    assert isinstance(BRANCH, str)
    assert isinstance(WHAT_TO_DEPLOY, str)
    assert isinstance(USE_KEYPAIRS_FILE, bool)
    assert isinstance(IMAGE_ID, str)
    assert isinstance(INSTANCE_TYPE, str)
except NameError as e:
    sys.exit('A variable with {} '.format(e.args[0]) + 'in deploy_conf.py')

if NUM_NODES > 64:
    raise ValueError('NUM_NODES should be less than or equal to 64. '
                     'The deploy_conf.py file sets it to {}'.format(NUM_NODES))

if WHAT_TO_DEPLOY not in ['servers', 'clients']:
    raise ValueError('WHAT_TO_DEPLOY should be either "servers" or "clients". '
                     'The deploy_conf.py file sets it to {}'.
                     format(WHAT_TO_DEPLOY))
