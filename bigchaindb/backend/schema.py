"""Schema-providing interfaces for backend databases"""

from functools import singledispatch


@singledispatch
def create_database(connection, name):
    raise NotImplementedError


@singledispatch
def create_tables(connection, name):
    raise NotImplementedError


@singledispatch
def create_indexes(connection, name):
    raise NotImplementedError


@singledispatch
def drop_database(connection, name):
    raise NotImplementedError
