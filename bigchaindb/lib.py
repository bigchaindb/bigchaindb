# Copyright © 2020 Interplanetary Database Association e.V.,
# BigchainDB and IPDB software contributors.
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

"""Module containing main contact points with Tendermint and
MongoDB.

"""
import logging
from collections import namedtuple
from uuid import uuid4

import rapidjson

try:
    from hashlib import sha3_256
except ImportError:
    # NOTE: neeeded for Python < 3.6
    from sha3 import sha3_256

import requests

import bigchaindb
from bigchaindb import backend, config_utils, fastquery
from bigchaindb.models import Transaction
from bigchaindb.common.exceptions import (SchemaValidationError,
                                          ValidationError,
                                          DoubleSpend)
from bigchaindb.common.transaction_mode_types import (BROADCAST_TX_COMMIT,
                                                      BROADCAST_TX_ASYNC,
                                                      BROADCAST_TX_SYNC)
from bigchaindb.tendermint_utils import encode_transaction, merkleroot
from bigchaindb import exceptions as core_exceptions
from bigchaindb.validation import BaseValidationRules


logger = logging.getLogger(__name__)


class BigchainDB(object):
    """Bigchain API

    Create, read, sign, write transactions to the database
    """

    def __init__(self, connection=None):
        """Initialize the Bigchain instance

        A Bigchain instance has several configuration parameters (e.g. host).
        If a parameter value is passed as an argument to the Bigchain
        __init__ method, then that is the value it will have.
        Otherwise, the parameter value will come from an environment variable.
        If that environment variable isn't set, then the value
        will come from the local configuration file. And if that variable
        isn't in the local configuration file, then the parameter will have
        its default value (defined in bigchaindb.__init__).

        Args:
            connection (:class:`~bigchaindb.backend.connection.Connection`):
                A connection to the database.
        """
        config_utils.autoconfigure()
        self.mode_commit = BROADCAST_TX_COMMIT
        self.mode_list = (BROADCAST_TX_ASYNC,
                          BROADCAST_TX_SYNC,
                          self.mode_commit)
        self.tendermint_host = bigchaindb.config['tendermint']['host']
        self.tendermint_port = bigchaindb.config['tendermint']['port']
        self.endpoint = 'http://{}:{}/'.format(self.tendermint_host, self.tendermint_port)

        validationPlugin = bigchaindb.config.get('validation_plugin')

        if validationPlugin:
            self.validation = config_utils.load_validation_plugin(validationPlugin)
        else:
            self.validation = BaseValidationRules

        self.connection = connection if connection else backend.connect(**bigchaindb.config['database'])

    def post_transaction(self, transaction, mode):
        """Submit a valid transaction to the mempool."""
        if not mode or mode not in self.mode_list:
            raise ValidationError('Mode must be one of the following {}.'
                                  .format(', '.join(self.mode_list)))

        tx_dict = transaction.tx_dict if transaction.tx_dict else transaction.to_dict()
        payload = {
            'method': mode,
            'jsonrpc': '2.0',
            'params': [encode_transaction(tx_dict)],
            'id': str(uuid4())
        }
        # TODO: handle connection errors!
        return requests.post(self.endpoint, json=payload)

    def write_transaction(self, transaction, mode):
        # This method offers backward compatibility with the Web API.
        """Submit a valid transaction to the mempool."""
        response = self.post_transaction(transaction, mode)
        return self._process_post_response(response.json(), mode)

    def _process_post_response(self, response, mode):
        logger.debug(response)

        error = response.get('error')
        if error:
            status_code = 500
            message = error.get('message', 'Internal Error')
            data = error.get('data', '')

            if 'Tx already exists in cache' in data:
                status_code = 400

            return (status_code, message + ' - ' + data)

        result = response['result']
        if mode == self.mode_commit:
            check_tx_code = result.get('check_tx', {}).get('code', 0)
            deliver_tx_code = result.get('deliver_tx', {}).get('code', 0)
            error_code = check_tx_code or deliver_tx_code
        else:
            error_code = result.get('code', 0)

        if error_code:
            return (500, 'Transaction validation failed')

        return (202, '')

    def store_bulk_transactions(self, transactions):
        txns = []
        assets = []
        txn_metadatas = []
        for t in transactions:
            transaction = t.tx_dict if t.tx_dict else rapidjson.loads(rapidjson.dumps(t.to_dict()))
            if transaction['operation'] == t.CREATE:
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

    def delete_transactions(self, txs):
        return backend.query.delete_transactions(self.connection, txs)

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

    def is_committed(self, transaction_id):
        transaction = backend.query.get_transaction(self.connection, transaction_id)
        return bool(transaction)

    def get_transaction(self, transaction_id):
        transaction = backend.query.get_transaction(self.connection, transaction_id)

        if transaction:
            asset = backend.query.get_asset(self.connection, transaction_id)
            metadata = backend.query.get_metadata(self.connection, [transaction_id])
            if asset:
                transaction['asset'] = asset

            if 'metadata' not in transaction:
                metadata = metadata[0] if metadata else None
                if metadata:
                    metadata = metadata.get('metadata')

                transaction.update({'metadata': metadata})

            transaction = Transaction.from_dict(transaction)

        return transaction

    def get_transactions(self, txn_ids):
        return backend.query.get_transactions(self.connection, txn_ids)

    def get_transactions_filtered(self, asset_id, operation=None, last_tx=None):
        """Get a list of transactions filtered on some criteria
        """
        txids = backend.query.get_txids_filtered(self.connection, asset_id,
                                                 operation, last_tx)
        for txid in txids:
            yield self.get_transaction(txid)

    def get_outputs_filtered(self, owner, spent=None):
        """Get a list of output links filtered on some criteria

        Args:
            owner (str): base58 encoded public_key.
            spent (bool): If ``True`` return only the spent outputs. If
                          ``False`` return only unspent outputs. If spent is
                          not specified (``None``) return all outputs.

        Returns:
            :obj:`list` of TransactionLink: list of ``txid`` s and ``output`` s
            pointing to another transaction's condition
        """
        outputs = self.fastquery.get_outputs_by_public_key(owner)
        if spent is None:
            return outputs
        elif spent is True:
            return self.fastquery.filter_unspent_outputs(outputs)
        elif spent is False:
            return self.fastquery.filter_spent_outputs(outputs)

    def get_spent(self, txid, output, current_transactions=[]):
        transactions = backend.query.get_spent(self.connection, txid,
                                               output)
        transactions = list(transactions) if transactions else []
        if len(transactions) > 1:
            raise core_exceptions.CriticalDoubleSpend(
                '`{}` was spent more than once. There is a problem'
                ' with the chain'.format(txid))

        current_spent_transactions = []
        for ctxn in current_transactions:
            for ctxn_input in ctxn.inputs:
                if ctxn_input.fulfills and\
                   ctxn_input.fulfills.txid == txid and\
                   ctxn_input.fulfills.output == output:
                    current_spent_transactions.append(ctxn)

        transaction = None
        if len(transactions) + len(current_spent_transactions) > 1:
            raise DoubleSpend('tx "{}" spends inputs twice'.format(txid))
        elif transactions:
            transaction = Transaction.from_db(self, transactions[0])
        elif current_spent_transactions:
            transaction = current_spent_transactions[0]

        return transaction

    def store_block(self, block):
        """Create a new block."""

        return backend.query.store_block(self.connection, block)

    def get_latest_block(self):
        """Get the block with largest height."""

        return backend.query.get_latest_block(self.connection)

    def get_block(self, block_id):
        """Get the block with the specified `block_id`.

        Returns the block corresponding to `block_id` or None if no match is
        found.

        Args:
            block_id (int): block id of the block to get.
        """

        block = backend.query.get_block(self.connection, block_id)
        latest_block = self.get_latest_block()
        latest_block_height = latest_block['height'] if latest_block else 0

        if not block and block_id > latest_block_height:
            return

        result = {'height': block_id,
                  'transactions': []}

        if block:
            transactions = backend.query.get_transactions(self.connection, block['transactions'])
            result['transactions'] = [t.to_dict() for t in Transaction.from_db(self, transactions)]

        return result

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
        if isinstance(transaction, dict):
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

    def text_search(self, search, *, limit=0, table='assets'):
        """Return an iterator of assets that match the text search

        Args:
            search (str): Text search string to query the text index
            limit (int, optional): Limit the number of returned documents.

        Returns:
            iter: An iterator of assets that match the text search.
        """
        return backend.query.text_search(self.connection, search, limit=limit,
                                         table=table)

    def get_assets(self, asset_ids):
        """Return a list of assets that match the asset_ids

        Args:
            asset_ids (:obj:`list` of :obj:`str`): A list of asset_ids to
                retrieve from the database.

        Returns:
            list: The list of assets returned from the database.
        """
        return backend.query.get_assets(self.connection, asset_ids)

    def get_metadata(self, txn_ids):
        """Return a list of metadata that match the transaction ids (txn_ids)

        Args:
            txn_ids (:obj:`list` of :obj:`str`): A list of txn_ids to
                retrieve from the database.

        Returns:
            list: The list of metadata returned from the database.
        """
        return backend.query.get_metadata(self.connection, txn_ids)

    @property
    def fastquery(self):
        return fastquery.FastQuery(self.connection)

    def get_validator_change(self, height=None):
        return backend.query.get_validator_set(self.connection, height)

    def get_validators(self, height=None):
        result = self.get_validator_change(height)
        return [] if result is None else result['validators']

    def get_election(self, election_id):
        return backend.query.get_election(self.connection, election_id)

    def get_pre_commit_state(self):
        return backend.query.get_pre_commit_state(self.connection)

    def store_pre_commit_state(self, state):
        return backend.query.store_pre_commit_state(self.connection, state)

    def store_validator_set(self, height, validators):
        """Store validator set at a given `height`.
           NOTE: If the validator set already exists at that `height` then an
           exception will be raised.
        """
        return backend.query.store_validator_set(self.connection, {'height': height,
                                                                   'validators': validators})

    def delete_validator_set(self, height):
        return backend.query.delete_validator_set(self.connection, height)

    def store_abci_chain(self, height, chain_id, is_synced=True):
        return backend.query.store_abci_chain(self.connection, height,
                                              chain_id, is_synced)

    def delete_abci_chain(self, height):
        return backend.query.delete_abci_chain(self.connection, height)

    def get_latest_abci_chain(self):
        return backend.query.get_latest_abci_chain(self.connection)

    def migrate_abci_chain(self):
        """Generate and record a new ABCI chain ID. New blocks are not
        accepted until we receive an InitChain ABCI request with
        the matching chain ID and validator set.

        Chain ID is generated based on the current chain and height.
        `chain-X` => `chain-X-migrated-at-height-5`.
        `chain-X-migrated-at-height-5` => `chain-X-migrated-at-height-21`.

        If there is no known chain (we are at genesis), the function returns.
        """
        latest_chain = self.get_latest_abci_chain()
        if latest_chain is None:
            return

        block = self.get_latest_block()

        suffix = '-migrated-at-height-'
        chain_id = latest_chain['chain_id']
        block_height_str = str(block['height'])
        new_chain_id = chain_id.split(suffix)[0] + suffix + block_height_str

        self.store_abci_chain(block['height'] + 1, new_chain_id, False)

    def store_election(self, election_id, height, is_concluded):
        return backend.query.store_election(self.connection, election_id,
                                            height, is_concluded)

    def store_elections(self, elections):
        return backend.query.store_elections(self.connection, elections)

    def delete_elections(self, height):
        return backend.query.delete_elections(self.connection, height)


Block = namedtuple('Block', ('app_hash', 'height', 'transactions'))
