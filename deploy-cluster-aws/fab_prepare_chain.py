#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Generating genesis block
"""

from __future__ import with_statement

from fabric import colors as c
from fabric.api import *
from fabric.api import local, puts, settings, hide, abort, lcd, prefix
from fabric.api import run, sudo, cd, get, local, lcd, env, hide
from fabric.api import task, parallel
from fabric.contrib import files
from fabric.contrib.files import append, exists
from fabric.contrib.console import confirm
from fabric.contrib.project import rsync_project
from fabric.operations import run, put
from fabric.context_managers import settings
from fabric.decorators import roles
from fabtools import *

env.user = 'ubuntu'
env.key_filename = 'pem/bigchaindb.pem'

@task
def init_bigchaindb():
    run('bigchaindb -y start &', pty = False)
