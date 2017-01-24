"""Database configuration functions."""
import logging

from pymongo.errors import OperationFailure

from bigchaindb.backend import admin
from bigchaindb.backend.utils import module_dispatch_registrar
from bigchaindb.backend.exceptions import DatabaseOpFailedError
from bigchaindb.backend.mongodb.connection import MongoDBConnection

logger = logging.getLogger(__name__)

register_admin = module_dispatch_registrar(admin)


@register_admin(MongoDBConnection)
def add_replicas(connection, replicas):
    """Add a set of replicas to the replicaset

    Args:
        replicas list of strings: of the form "hostname:port".
    """
    # get current configuration
    conf = connection.conn.admin.command('replSetGetConfig')

    # MongoDB does not automatically add and id for the members so we need
    # to chose one that does not exists yet. The safest way is to use
    # incrementing ids, so we first check what is the highest id already in
    # the set and continue from there.
    cur_id = max([member['_id'] for member in conf['config']['members']])

    # add the nodes to the members list of the replica set
    for replica in replicas:
        cur_id += 1
        conf['config']['members'].append({'_id': cur_id, 'host': replica})

    # increase the configuration version number
    conf['config']['version'] += 1

    # apply new configuration
    try:
        return connection.conn.admin.command('replSetReconfig', conf['config'])
    except OperationFailure as exc:
        raise DatabaseOpFailedError(exc.details['errmsg'])


@register_admin(MongoDBConnection)
def remove_replicas(connection, replicas):
    """Remove a set of replicas from the replicaset

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
        return connection.conn.admin.command('replSetReconfig', conf['config'])
    except OperationFailure as exc:
        raise DatabaseOpFailedError(exc.details['errmsg'])
