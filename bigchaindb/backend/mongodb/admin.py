"""Database configuration functions."""
import logging

from pymongo.errors import OperationFailure

from bigchaindb.backend import admin
from bigchaindb.backend.utils import module_dispatch_registrar
from bigchaindb.backend.exceptions import OperationError
from bigchaindb.backend.mongodb.connection import MongoDBConnection

logger = logging.getLogger(__name__)

register_admin = module_dispatch_registrar(admin)


@register_admin(MongoDBConnection)
def add_replicas(connection, replicas):
    """Add a set of replicas to the replicaset

    Args:
        connection (:class:`~bigchaindb.backend.connection.Connection`):
            A connection to the database.
        replicas (:obj:`list` of :obj:`str`): replica addresses in the
            form "hostname:port".

    Raises:
        OperationError: If the reconfiguration fails due to a MongoDB
            :exc:`OperationFailure`
    """
    # get current configuration
    conf = connection.conn.admin.command('replSetGetConfig')

    # MongoDB does not automatically add an id for the members so we need
    # to choose one that does not exist yet. The safest way is to use
    # incrementing ids, so we first check what is the highest id already in
    # the set and continue from there.
    cur_id = max([member['_id'] for member in conf['config']['members']])

    # add the nodes to the members list of the replica set
    for replica in replicas:
        cur_id += 1
        conf['config']['members'].append({'_id': cur_id, 'host': replica})

    # increase the configuration version number
    # when reconfiguring, mongodb expects a version number higher than the one
    # it currently has
    conf['config']['version'] += 1

    # apply new configuration
    try:
        connection.conn.admin.command('replSetReconfig', conf['config'])
    except OperationFailure as exc:
        raise OperationError(exc.details['errmsg'])


@register_admin(MongoDBConnection)
def remove_replicas(connection, replicas):
    """Remove a set of replicas from the replicaset

    Args:
        connection (:class:`~bigchaindb.backend.connection.Connection`):
            A connection to the database.
        replicas (:obj:`list` of :obj:`str`): replica addresses in the
            form "hostname:port".

    Raises:
        OperationError: If the reconfiguration fails due to a MongoDB
            :exc:`OperationFailure`
    """
    # get the current configuration
    conf = connection.conn.admin.command('replSetGetConfig')

    # remove the nodes from the members list in the replica set
    conf['config']['members'] = list(
        filter(lambda member: member['host'] not in replicas,
               conf['config']['members'])
    )

    # increase the configuration version number
    conf['config']['version'] += 1

    # apply new configuration
    try:
        connection.conn.admin.command('replSetReconfig', conf['config'])
    except OperationFailure as exc:
        raise OperationError(exc.details['errmsg'])
