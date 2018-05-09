"""Module containing main contact points with Tendermint and
MongoDB.

"""
import logging
from collections import namedtuple
from copy import deepcopy
from os import getenv
from uuid import uuid4

try:
    from hashlib import sha3_256
except ImportError:
    # NOTE: neeeded for Python < 3.6
    from sha3 import sha3_256

import requests

from bigchaindb import backend
from bigchaindb import Bigchain
from bigchaindb.models import Transaction
from bigchaindb.common.exceptions import (SchemaValidationError,
                                          ValidationError,
                                          DoubleSpend)
from bigchaindb.tendermint.utils import encode_transaction, merkleroot
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
        return requests.post(ENDPOINT, json=payload)

    def write_transaction(self, transaction, mode):
        # This method offers backward compatibility with the Web API.
        """Submit a valid transaction to the mempool."""
        response = self.post_transaction(transaction, mode)
        return self._process_post_response(response.json(), mode)

    def _process_post_response(self, response, mode):
        logger.debug(response)
        if response.get('error') is not None:
            return (500, 'Internal error')

        return (202, '')
        # result = response['result']
        # if mode == MODE_LIST[2]:
        #     return self._process_commit_mode_response(result)
        # else:
        #     status_code = result['code']
        #     return self._process_status_code(status_code,
        #                                      'Error while processing transaction')

    # def _process_commit_mode_response(self, result):
    #     check_tx_status_code = result['check_tx']['code']
    #     if check_tx_status_code == 0:
    #         deliver_tx_status_code = result['deliver_tx']['code']
    #         return self._process_status_code(deliver_tx_status_code,
    #                                          'Error while commiting the transaction')
    #     else:
    #         return (500, 'Error while validating the transaction')

    def _process_status_code(self, status_code, failure_msg):
        return (202, '') if status_code == 0 else (500, failure_msg)

    def get_latest_block_height_from_tendermint(self):
        r = requests.get(ENDPOINT + 'status')
        return r.json()['result']['latest_block_height']

    def store_transaction(self, transaction):
        """Store a valid transaction to the transactions collection."""

        # self.update_utxoset(transaction)
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
            # self.update_utxoset(transaction)
            transaction = transaction.to_dict()
            if transaction['operation'] == 'CREATE':
                asset = transaction.pop('asset')
                asset['id'] = transaction['id']
                assets.append(asset)

            metadata = transaction.pop('metadata')
            txn_metadatas.append({'id': transaction['id'],
                                  'metadata': metadata})
            txns.append(transaction)

        backend.query.store_metadatas(self.connection, txn_metadatas)
        if assets:
            backend.query.store_assets(self.connection, assets)
        return backend.query.store_transactions(self.connection, txns)

    def update_utxoset(self, transaction):
        """Update the UTXO set given ``transaction``. That is, remove
        the outputs that the given ``transaction`` spends, and add the
        outputs that the given ``transaction`` creates.

        Args:
            transaction (:obj:`~bigchaindb.models.Transaction`): A new
                transaction incoming into the system for which the UTXO
                set needs to be updated.
        """
        spent_outputs = [
            spent_output for spent_output in transaction.spent_outputs
        ]
        if spent_outputs:
            self.delete_unspent_outputs(*spent_outputs)
        self.store_unspent_outputs(
            *[utxo._asdict() for utxo in transaction.unspent_outputs]
        )

    def store_unspent_outputs(self, *unspent_outputs):
        """Store the given ``unspent_outputs`` (utxos).

        Args:
            *unspent_outputs (:obj:`tuple` of :obj:`dict`): Variable
                length tuple or list of unspent outputs.
        """
        if unspent_outputs:
            return backend.query.store_unspent_outputs(
                                            self.connection, *unspent_outputs)

    def get_utxoset_merkle_root(self):
        """Returns the merkle root of the utxoset. This implies that
        the utxoset is first put into a merkle tree.

        For now, the merkle tree and its root will be computed each
        time. This obviously is not efficient and a better approach
        that limits the repetition of the same computation when
        unnecesary should be sought. For instance, future optimizations
        could simply re-compute the branches of the tree that were
        affected by a change.

        The transaction hash (id) and output index should be sufficient
        to uniquely identify a utxo, and consequently only that
        information from a utxo record is needed to compute the merkle
        root. Hence, each node of the merkle tree should contain the
        tuple (txid, output_index).

        .. important:: The leaves of the tree will need to be sorted in
            some kind of lexicographical order.

        Returns:
            str: Merkle root in hexadecimal form.
        """
        utxoset = backend.query.get_unspent_outputs(self.connection)
        # TODO Once ready, use the already pre-computed utxo_hash field.
        # See common/transactions.py for details.
        hashes = [
            sha3_256(
                '{}{}'.format(utxo['transaction_id'], utxo['output_index']).encode()
            ).digest() for utxo in utxoset
        ]
        # TODO Notice the sorted call!
        return merkleroot(sorted(hashes))

    def get_unspent_outputs(self):
        """Get the utxoset.

        Returns:
            generator of unspent_outputs.
        """
        cursor = backend.query.get_unspent_outputs(self.connection)
        return (record for record in cursor)

    def delete_unspent_outputs(self, *unspent_outputs):
        """Deletes the given ``unspent_outputs`` (utxos).

        Args:
            *unspent_outputs (:obj:`tuple` of :obj:`dict`): Variable
                length tuple or list of unspent outputs.
        """
        if unspent_outputs:
            return backend.query.delete_unspent_outputs(
                                        self.connection, *unspent_outputs)

    def get_transaction(self, transaction_id, include_status=False):
        transaction = backend.query.get_transaction(self.connection, transaction_id)
        asset = backend.query.get_asset(self.connection, transaction_id)
        metadata = backend.query.get_metadata(self.connection, [transaction_id])

        if transaction:
            if asset:
                transaction['asset'] = asset

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
        if len(transactions) > 1:
            raise core_exceptions.CriticalDoubleSpend(
                '`{}` was spent more than once. There is a problem'
                ' with the chain'.format(txid))

        for ctxn in current_transactions:
            for ctxn_input in ctxn.inputs:
                if ctxn_input.fulfills.txid == txid and\
                   ctxn_input.fulfills.output == output:
                    transactions.append(ctxn.to_dict())

        transaction = None
        if len(transactions) > 1:
            raise DoubleSpend('tx "{}" spends inputs twice'.format(txid))
        elif transactions:
            transaction = Transaction.from_db(self, transactions[0])

        return transaction

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

        # CLEANUP: The conditional below checks for transaction in dict format.
        # It would be better to only have a single format for the transaction
        # throught the code base.
        if not isinstance(transaction, Transaction):
            try:
                transaction = Transaction.from_dict(tx)
            except SchemaValidationError as e:
                logger.warning('Invalid transaction schema: %s', e.__cause__.message)
                return False
            except ValidationError as e:
                logger.warning('Invalid transaction (%s): %s', type(e).__name__, e)
                return False
        return transaction.validate(self, current_transactions)

    def is_valid_transaction(self, tx, current_transactions=[]):
        # NOTE: the function returns the Transaction object in case
        # the transaction is valid
        try:
            return self.validate_transaction(tx, current_transactions)
        except ValidationError as e:
            logger.warning('Invalid transaction (%s): %s', type(e).__name__, e)
            return False

    @property
    def fastquery(self):
        return fastquery.FastQuery(self.connection)

    def get_validators(self):
        try:
            resp = requests.get('{}validators'.format(ENDPOINT))
            validators = resp.json()['result']['validators']
            for v in validators:
                v.pop('accum')
                v.pop('address')

            return validators

        except requests.exceptions.RequestException as e:
            logger.error('Error while connecting to Tendermint HTTP API')
            raise e

    def get_validator_update(self):
        update = backend.query.get_validator_update(self.connection)
        return [update['validator']] if update else []

    def delete_validator_update(self):
        return backend.query.delete_validator_update(self.connection)

    def store_pre_commit_state(self, state):
        return backend.query.store_pre_commit_state(self.connection, state)


Block = namedtuple('Block', ('app_hash', 'height', 'transactions'))

PreCommitState = namedtuple('PreCommitState', ('commit_id', 'height', 'transactions'))
