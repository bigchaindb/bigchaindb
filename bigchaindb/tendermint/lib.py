import logging
from collections import namedtuple
from copy import deepcopy
from os import getenv
from uuid import uuid4

import requests

from bigchaindb import backend
from bigchaindb import Bigchain
from bigchaindb.models import Transaction
from bigchaindb.common.exceptions import SchemaValidationError, ValidationError
from bigchaindb.tendermint.utils import encode_transaction
from bigchaindb.tendermint import fastquery
from bigchaindb import exceptions as core_exceptions


logger = logging.getLogger(__name__)

BIGCHAINDB_TENDERMINT_HOST = getenv('BIGCHAINDB_TENDERMINT_HOST',
                                    'localhost')
BIGCHAINDB_TENDERMINT_PORT = getenv('BIGCHAINDB_TENDERMINT_PORT',
                                    '46657')
ENDPOINT = 'http://{}:{}/'.format(BIGCHAINDB_TENDERMINT_HOST,
                                  BIGCHAINDB_TENDERMINT_PORT)
MODE_LIST = ('broadcast_tx_async',
             'broadcast_tx_sync',
             'broadcast_tx_commit')


class BigchainDB(Bigchain):

    def post_transaction(self, transaction, mode):
        """Submit a valid transaction to the mempool."""
        if not mode or mode not in MODE_LIST:
            raise ValidationError(('Mode must be one of the following {}.')
                                  .format(', '.join(MODE_LIST)))

        payload = {
            'method': mode,
            'jsonrpc': '2.0',
            'params': [encode_transaction(transaction.to_dict())],
            'id': str(uuid4())
        }
        # TODO: handle connection errors!
        requests.post(ENDPOINT, json=payload)

    def write_transaction(self, transaction, mode):
        # This method offers backward compatibility with the Web API.
        """Submit a valid transaction to the mempool."""
        self.post_transaction(transaction, mode)

    def store_transaction(self, transaction):
        """Store a valid transaction to the transactions collection."""

        transaction = deepcopy(transaction.to_dict())
        if transaction['operation'] == 'CREATE':
            asset = transaction.pop('asset')
            asset['id'] = transaction['id']
            if asset['data']:
                backend.query.store_asset(self.connection, asset)

        metadata = transaction.pop('metadata')
        transaction_metadata = {'id': transaction['id'],
                                'metadata': metadata}

        backend.query.store_metadatas(self.connection, [transaction_metadata])

        return backend.query.store_transaction(self.connection, transaction)

    def store_bulk_transactions(self, transactions):
        txns = []
        assets = []
        txn_metadatas = []
        for transaction in transactions:
            transaction = transaction.to_dict()
            if transaction['operation'] == 'CREATE':
                asset = transaction.pop('asset')
                asset['id'] = transaction['id']
                if asset['data'] is not None:
                    assets.append(asset)

            metadata = transaction.pop('metadata')
            txn_metadatas.append({'id': transaction['id'],
                                  'metadata': metadata})
            txns.append(transaction)

        backend.query.store_metadatas(self.connection, txn_metadatas)
        if assets:
            backend.query.store_assets(self.connection, assets)
        return backend.query.store_transactions(self.connection, txns)

    def get_transaction(self, transaction_id, include_status=False):
        transaction = backend.query.get_transaction(self.connection, transaction_id)
        asset = backend.query.get_asset(self.connection, transaction_id)
        metadata = backend.query.get_metadata(self.connection, [transaction_id])

        if transaction:
            if asset:
                transaction['asset'] = asset
            else:
                transaction['asset'] = {'data': None}

            if 'metadata' not in transaction:
                metadata = metadata[0] if metadata else None
                if metadata:
                    metadata = metadata.get('metadata')

                transaction.update({'metadata': metadata})

            transaction = Transaction.from_dict(transaction)

        if include_status:
            return transaction, self.TX_VALID if transaction else None
        else:
            return transaction

    def get_spent(self, txid, output, current_transactions=[]):
        transactions = backend.query.get_spent(self.connection, txid,
                                               output)
        transactions = list(transactions) if transactions else []

        for ctxn in current_transactions:
            for ctxn_input in ctxn.inputs:
                if ctxn_input.fulfills.txid == txid and\
                   ctxn_input.fulfills.output == output:
                    transactions.append(ctxn.to_dict())

        transaction = None
        if len(transactions) > 1:
            raise core_exceptions.CriticalDoubleSpend(
                '`{}` was spent more than once. There is a problem'
                ' with the chain'.format(txid))
        elif transactions:
            transaction = transactions[0]

        if transaction and transaction['operation'] == 'CREATE':
            asset = backend.query.get_asset(self.connection, transaction['id'])

            if asset:
                transaction['asset'] = asset
            else:
                transaction['asset'] = {'data': None}

            return Transaction.from_dict(transaction)
        elif transaction and transaction['operation'] == 'TRANSFER':
            return Transaction.from_dict(transaction)
        else:
            return None

    def store_block(self, block):
        """Create a new block."""

        return backend.query.store_block(self.connection, block)

    def get_latest_block(self):
        """Get the block with largest height."""

        return backend.query.get_latest_block(self.connection)

    def get_block(self, block_id, include_status=False):
        """Get the block with the specified `block_id` (and optionally its status)

        Returns the block corresponding to `block_id` or None if no match is
        found.

        Args:
            block_id (str): block id of the block to get
            include_status (bool): also return the status of the block
                       the return value is then a tuple: (block, status)
        """
        # get block from database
        if isinstance(block_id, str):
            block_id = int(block_id)

        block = backend.query.get_block(self.connection, block_id)
        if block:
            transactions = backend.query.get_transactions(self.connection, block['transactions'])
            transactions = Transaction.from_db(self, transactions)

            block = {'height': block['height'],
                     'transactions': []}
            block_txns = block['transactions']
            for txn in transactions:
                block_txns.append(txn.to_dict())

        status = None
        if include_status:
            # NOTE: (In Tendermint) a block is an abstract entity which
            # exists only after it has been validated
            if block:
                status = self.BLOCK_VALID
            return block, status
        else:
            return block

    def get_block_containing_tx(self, txid):
        """Retrieve the list of blocks (block ids) containing a
           transaction with transaction id `txid`

        Args:
            txid (str): transaction id of the transaction to query

        Returns:
            Block id list (list(int))
        """
        blocks = list(backend.query.get_block_with_transaction(self.connection, txid))
        if len(blocks) > 1:
            logger.critical('Transaction id %s exists in multiple blocks', txid)

        return [block['height'] for block in blocks]

    def validate_transaction(self, tx, current_transactions=[]):
        """Validate a transaction against the current status of the database."""

        transaction = tx

        if not isinstance(transaction, Transaction):
            try:
                transaction = Transaction.from_dict(tx)
            except SchemaValidationError as e:
                logger.warning('Invalid transaction schema: %s', e.__cause__.message)
                return False
            except ValidationError as e:
                logger.warning('Invalid transaction (%s): %s', type(e).__name__, e)
                return False
        try:
            return transaction.validate(self, current_transactions)
        except ValidationError as e:
            logger.warning('Invalid transaction (%s): %s', type(e).__name__, e)
            return False
        return transaction

    @property
    def fastquery(self):
        return fastquery.FastQuery(self.connection, self.me)


Block = namedtuple('Block', ('app_hash', 'height', 'transactions'))
