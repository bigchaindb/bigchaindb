"""Database configuration functions."""
from functools import singledispatch


@singledispatch
def get_config(connection, *, table):
    raise NotImplementedError


@singledispatch
def reconfigure(connection, *, table, shards, replicas, **kwargs):
    raise NotImplementedError


@singledispatch
def set_shards(connection, *, shards):
    raise NotImplementedError


@singledispatch
def set_replicas(connection, *, replicas):
    raise NotImplementedError


@singledispatch
def add_replicas(connection, replicas):
    raise NotImplementedError('This command is specific to the '
                              'MongoDB backend.')


@singledispatch
def remove_replicas(connection, replicas):
    raise NotImplementedError('This command is specific to the '
                              'MongoDB backend.')
