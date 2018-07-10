"""Utils to initialize and drop the database."""

import logging

from pymongo import ASCENDING, DESCENDING, TEXT

from bigchaindb import backend
from bigchaindb.common import exceptions
from bigchaindb.backend.utils import module_dispatch_registrar
from bigchaindb.backend.localmongodb.connection import LocalMongoDBConnection


logger = logging.getLogger(__name__)
register_schema = module_dispatch_registrar(backend.schema)


@register_schema(LocalMongoDBConnection)
def create_database(conn, dbname):
    if dbname in conn.conn.database_names():
        raise exceptions.DatabaseAlreadyExists('Database `{}` already exists'
                                               .format(dbname))

    logger.info('Create database `%s`.', dbname)
    # TODO: read and write concerns can be declared here
    conn.conn.get_database(dbname)


@register_schema(LocalMongoDBConnection)
def create_tables(conn, dbname):
    for table_name in ['transactions', 'utxos', 'assets', 'blocks', 'metadata',
                       'validators', 'pre_commit']:
        logger.info('Create `%s` table.', table_name)
        # create the table
        # TODO: read and write concerns can be declared here
        conn.conn[dbname].create_collection(table_name)


@register_schema(LocalMongoDBConnection)
def create_indexes(conn, dbname):
    create_transactions_secondary_index(conn, dbname)
    create_assets_secondary_index(conn, dbname)
    create_blocks_secondary_index(conn, dbname)
    create_metadata_secondary_index(conn, dbname)
    create_utxos_secondary_index(conn, dbname)
    create_pre_commit_secondary_index(conn, dbname)
    create_validators_secondary_index(conn, dbname)


@register_schema(LocalMongoDBConnection)
def drop_database(conn, dbname):
    conn.conn.drop_database(dbname)


def create_transactions_secondary_index(conn, dbname):
    logger.info('Create `transactions` secondary index.')

    # to query the transactions for a transaction id, this field is unique
    conn.conn[dbname]['transactions'].create_index('id',
                                                   name='transaction_id')

    # secondary index for asset uuid, this field is unique
    conn.conn[dbname]['transactions']\
        .create_index('asset.id', name='asset_id')

    # secondary index on the public keys of outputs
    conn.conn[dbname]['transactions']\
        .create_index('outputs.public_keys',
                      name='outputs')

    # secondary index on inputs/transaction links (transaction_id, output)
    conn.conn[dbname]['transactions']\
        .create_index([
            ('inputs.fulfills.transaction_id', ASCENDING),
            ('inputs.fulfills.output_index', ASCENDING),
        ], name='inputs')


def create_assets_secondary_index(conn, dbname):
    logger.info('Create `assets` secondary index.')

    # unique index on the id of the asset.
    # the id is the txid of the transaction that created the asset
    conn.conn[dbname]['assets'].create_index('id',
                                             name='asset_id',
                                             unique=True)

    # full text search index
    conn.conn[dbname]['assets'].create_index([('$**', TEXT)], name='text')


def create_blocks_secondary_index(conn, dbname):
    conn.conn[dbname]['blocks']\
        .create_index([('height', DESCENDING)], name='height')


def create_metadata_secondary_index(conn, dbname):
    logger.info('Create `assets` secondary index.')

    # the id is the txid of the transaction where metadata was defined
    conn.conn[dbname]['metadata'].create_index('id',
                                               name='transaction_id',
                                               unique=True)

    # full text search index
    conn.conn[dbname]['metadata'].create_index([('$**', TEXT)], name='text')


def create_utxos_secondary_index(conn, dbname):
    logger.info('Create `utxos` secondary index.')

    conn.conn[dbname]['utxos'].create_index(
        [('transaction_id', ASCENDING), ('output_index', ASCENDING)],
        name='utxo',
        unique=True,
    )


def create_pre_commit_secondary_index(conn, dbname):
    logger.info('Create `pre_commit` secondary index.')

    conn.conn[dbname]['pre_commit'].create_index('commit_id',
                                                 name='pre_commit_id',
                                                 unique=True)


def create_validators_secondary_index(conn, dbname):
    logger.info('Create `validators` secondary index.')

    conn.conn[dbname]['validators'].create_index('update_id',
                                                 name='update_id',
                                                 unique=True,)
