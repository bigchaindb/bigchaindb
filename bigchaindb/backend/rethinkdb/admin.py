"""Database configuration functions."""
import logging

import rethinkdb as r

from bigchaindb.backend import admin
from bigchaindb.backend.schema import TABLES
from bigchaindb.backend.exceptions import OperationError
from bigchaindb.backend.utils import module_dispatch_registrar
from bigchaindb.backend.rethinkdb.connection import RethinkDBConnection

logger = logging.getLogger(__name__)

register_admin = module_dispatch_registrar(admin)


@register_admin(RethinkDBConnection)
def get_config(connection, *, table):
    """Get the configuration of the given table.

    Args:
        connection (:class:`~bigchaindb.backend.connection.Connection`):
            A connection to the database.
        table (str): The name of the table to get the configuration for.

    Returns:
        dict: The configuration of the given table

    """
    return connection.run(r.table(table).config())


@register_admin(RethinkDBConnection)
def reconfigure(connection, *, table, shards, replicas,
                primary_replica_tag=None, dry_run=False,
                nonvoting_replica_tags=None):
    """Reconfigures the given table.

    Args:
        connection (:class:`~bigchaindb.backend.connection.Connection`):
            A connection to the database.
        table (str): The name of the table to reconfigure.
        shards (int): The number of shards, an integer from 1-64.
        replicas (:obj:`int` | :obj:`dict`):
            * If replicas is an integer, it specifies the number of
              replicas per shard. Specifying more replicas than there
              are servers will return an error.
            * If replicas is a dictionary, it specifies key-value pairs
              of server tags and the number of replicas to assign to
              those servers::

                  {'africa': 2, 'asia': 4, 'europe': 2, ...}
        primary_replica_tag (str): The primary server specified by its
            server tag. Required if ``replicas`` is a dictionary. The
            tag must be in the ``replicas`` dictionary. This must not be
            specified if ``replicas`` is an integer. Defaults to
            ``None``.
        dry_run (bool): If ``True`` the generated configuration will not
            be applied to the table, only returned. Defaults to
            ``False``.
        nonvoting_replica_tags (:obj:`list` of :obj:`str`): Replicas
            with these server tags will be added to the
            ``nonvoting_replicas`` list of the resulting configuration.
            Defaults to ``None``.

    Returns:
        dict: A dictionary with possibly three keys:

            * ``reconfigured``: the number of tables reconfigured. This
              will be ``0`` if ``dry_run`` is ``True``.
            * ``config_changes``: a list of new and old table
              configuration values.
            * ``status_changes``: a list of new and old table status
              values.

            For more information please consult RethinkDB's
            documentation `ReQL command: reconfigure
            <https://rethinkdb.com/api/python/reconfigure/>`_.

    Raises:
        OperationError: If the reconfiguration fails due to a
            RethinkDB :exc:`ReqlOpFailedError` or
            :exc:`ReqlQueryLogicError`.

    """
    params = {
        'shards': shards,
        'replicas': replicas,
        'dry_run': dry_run,
    }
    if primary_replica_tag:
        params.update(
            primary_replica_tag=primary_replica_tag,
            nonvoting_replica_tags=nonvoting_replica_tags,
        )
    try:
        return connection.run(r.table(table).reconfigure(**params))
    except (r.ReqlOpFailedError, r.ReqlQueryLogicError) as e:
        raise OperationError('Failed to reconfigure tables.') from e


@register_admin(RethinkDBConnection)
def set_shards(connection, *, shards, dry_run=False):
    """Sets the shards for the tables
    :const:`~bigchaindb.backend.schema.TABLES`.

    Args:
        connection (:class:`~bigchaindb.backend.connection.Connection`):
            A connection to the database.
        shards (int): The number of shards, an integer from 1-64.
        dry_run (bool): If ``True`` the generated configuration will not
            be applied to the table, only returned. Defaults to
            ``False``.

    Returns:
        dict: A dictionary with the configuration and status changes.
            For more details please see :func:`.reconfigure`.

    """
    changes = {}
    for table in TABLES:
        replicas = len(
            get_config(connection, table=table)['shards'][0]['replicas'])
        change = reconfigure(
            connection,
            table=table,
            shards=shards,
            replicas=replicas,
            dry_run=dry_run,
        )
        changes[table] = change
    return changes


@register_admin(RethinkDBConnection)
def set_replicas(connection, *, replicas, dry_run=False):
    """Sets the replicas for the tables
    :const:`~bigchaindb.backend.schema.TABLES`.

    Args:
        connection (:class:`~bigchaindb.backend.connection.Connection`):
            A connection to the database.
        replicas (int): The number of replicas per shard. Specifying
            more replicas than there are servers will return an error.
        dry_run (bool): If ``True`` the generated configuration will not
            be applied to the table, only returned. Defaults to
            ``False``.

    Returns:
        dict: A dictionary with the configuration and status changes.
            For more details please see :func:`.reconfigure`.

    """
    changes = {}
    for table in TABLES:
        shards = len(get_config(connection, table=table)['shards'])
        change = reconfigure(
            connection,
            table=table,
            shards=shards,
            replicas=replicas,
            dry_run=dry_run,
        )
        changes[table] = change
    return changes
