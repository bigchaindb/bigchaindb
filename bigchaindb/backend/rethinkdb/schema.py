"""Utils to initialize and drop the database."""

import logging

from bigchaindb.db import Schema
from bigchaindb.common import exceptions
import rethinkdb as r


logger = logging.getLogger(__name__)


class RethinkDBSchema(Schema):

    def __init__(self, connection, name):
        self.connection = connection
        self.name = name

    def create_database(self):
        if self.connection.run(r.db_list().contains(self.name)):
            raise exceptions.DatabaseAlreadyExists('Database `{}` already exists'.format(self.name))

        logger.info('Create database `%s`.', self.name)
        self.connection.run(r.db_create(self.name))

    def create_tables(self):
        for table_name in ['bigchain', 'backlog', 'votes']:
            logger.info('Create `%s` table.', table_name)
            self.connection.run(r.db(self.name).table_create(table_name))

    def create_indexes(self):
        self.create_bigchain_secondary_index()

    def drop_database(self):
        try:
            logger.info('Drop database `%s`', self.name)
            self.connection.run(r.db_drop(self.name))
            logger.info('Done.')
        except r.ReqlOpFailedError:
            raise exceptions.DatabaseDoesNotExist('Database `{}` does not exist'.format(self.name))

    def create_bigchain_secondary_index(self):
        logger.info('Create `bigchain` secondary index.')

        # to order blocks by timestamp
        self.connection.run(
            r.db(self.name)
            .table('bigchain')
            .index_create('block_timestamp', r.row['block']['timestamp']))

        # to query the bigchain for a transaction id
        self.connection.run(
            r.db(self.name)
            .table('bigchain')
            .index_create('transaction_id', r.row['block']['transactions']['id'], multi=True))

        # secondary index for payload data by UUID
        self.connection.run(
            r.db(self.name)
            .table('bigchain')
            .index_create('metadata_id', r.row['block']['transactions']['transaction']['metadata']['id'], multi=True))

        # secondary index for asset uuid
        self.connection.run(
            r.db(self.name)
            .table('bigchain')
            .index_create('asset_id', r.row['block']['transactions']['transaction']['asset']['id'], multi=True))

        # wait for rethinkdb to finish creating secondary indexes
        self.connection.run(
            r.db(self.name)
            .table('bigchain')
            .index_wait())

    def create_backlog_secondary_index(self):
        logger.info('Create `backlog` secondary index.')

        # compound index to read transactions from the backlog per assignee
        self.connection.run(
            r.db(self.name)
            .table('backlog')
            .index_create('assignee__transaction_timestamp', [r.row['assignee'], r.row['assignment_timestamp']]))

        # wait for rethinkdb to finish creating secondary indexes
        self.connection.run(
            r.db(self.name)
            .table('backlog')
            .index_wait())

    def create_votes_secondary_index(self):
        logger.info('Create `votes` secondary index.')

        # compound index to order votes by block id and node
        self.connection.run(
            r.db(self.name)
            .table('votes')\
            .index_create('block_and_voter', [r.row['vote']['voting_for_block'], r.row['node_pubkey']]))

        # wait for rethinkdb to finish creating secondary indexes
        self.connection.run(
            r.db(self.name)
            .table('votes')
            .index_wait())
