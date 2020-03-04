# Copyright © 2020 Interplanetary Database Association e.V.,
# BigchainDB and IPDB software contributors.
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

"""Utils to initialize and drop the database."""

import logging

from pymongo import ASCENDING, DESCENDING, TEXT
from pymongo.errors import CollectionInvalid

from bigchaindb import backend
from bigchaindb.backend.utils import module_dispatch_registrar
from bigchaindb.backend.localmongodb.connection import LocalMongoDBConnection


logger = logging.getLogger(__name__)
register_schema = module_dispatch_registrar(backend.schema)


INDEXES = {
    'transactions': [
        ('id', dict(unique=True, name='transaction_id')),
        ('asset.id', dict(name='asset_id')),
        ('outputs.public_keys', dict(name='outputs')),
        ([('inputs.fulfills.transaction_id', ASCENDING),
          ('inputs.fulfills.output_index', ASCENDING)], dict(name='inputs')),
    ],
    'assets': [
        ('id', dict(name='asset_id', unique=True)),
        ([('$**', TEXT)], dict(name='text')),
    ],
    'blocks': [
        ([('height', DESCENDING)], dict(name='height', unique=True)),
    ],
    'metadata': [
        ('id', dict(name='transaction_id', unique=True)),
        ([('$**', TEXT)], dict(name='text')),
    ],
    'utxos': [
        ([('transaction_id', ASCENDING),
          ('output_index', ASCENDING)], dict(name='utxo', unique=True)),
    ],
    'pre_commit': [
        ('height', dict(name='height', unique=True)),
    ],
    'elections': [
        ([('height', DESCENDING), ('election_id', ASCENDING)],
         dict(name='election_id_height', unique=True)),
    ],
    'validators': [
        ('height', dict(name='height', unique=True)),
    ],
    'abci_chains': [
        ('height', dict(name='height', unique=True)),
        ('chain_id', dict(name='chain_id', unique=True)),
    ],
}


@register_schema(LocalMongoDBConnection)
def create_database(conn, dbname):
    logger.info('Create database `%s`.', dbname)
    # TODO: read and write concerns can be declared here
    conn.conn.get_database(dbname)


@register_schema(LocalMongoDBConnection)
def create_tables(conn, dbname):
    for table_name in backend.schema.TABLES:
        # create the table
        # TODO: read and write concerns can be declared here
        try:
            logger.info(f'Create `{table_name}` table.')
            conn.conn[dbname].create_collection(table_name)
        except CollectionInvalid:
            logger.info(f'Collection {table_name} already exists.')
        create_indexes(conn, dbname, table_name, INDEXES[table_name])


def create_indexes(conn, dbname, collection, indexes):
    logger.info(f'Ensure secondary indexes for `{collection}`.')
    for fields, kwargs in indexes:
        conn.conn[dbname][collection].create_index(fields, **kwargs)


@register_schema(LocalMongoDBConnection)
def drop_database(conn, dbname):
    conn.conn.drop_database(dbname)
