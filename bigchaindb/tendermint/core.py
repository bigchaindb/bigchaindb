"""This module contains all the goodness to integrate BigchainDB
with Tendermint."""


from abci import BaseApplication, Result

from bigchaindb.tendermint import BigchainDB
from bigchaindb.tendermint.utils import decode_transaction, calculate_hash


class App(BaseApplication):
    """Bridge between BigchainDB and Tendermint.

    The role of this class is to expose the BigchainDB
    transactional logic to the Tendermint Consensus
    State Machine."""

    def __init__(self, bigchaindb=None):
        if not bigchaindb:
            bigchaindb = BigchainDB()
        self.bigchaindb = bigchaindb
        self.block_txn_ids = []

    def check_tx(self, raw_transaction):
        """Validate the transaction before entry into
        the mempool.

        Args:
            raw_tx: a raw string (in bytes) transaction."""

        transaction = decode_transaction(raw_transaction)
        if self.bigchaindb.validate_transaction(transaction):
            return Result.ok()
        else:
            return Result.error()

    def begin_block(self, block_hash, header):
        self.block_txn_ids = []

    def deliver_tx(self, raw_transaction):
        """Validate the transaction before mutating the state.

        Args:
            raw_tx: a raw string (in bytes) transaction."""

        transaction = self.bigchaindb.validate_transaction(
                decode_transaction(raw_transaction))

        if not transaction:
            return Result.error(log='Invalid transaction')
        else:
            self.bigchaindb.store_transaction(transaction)
            self.block_txn_ids.append(transaction.to_dict()['id'])
            return Result.ok()

    def commit(self):
        """ Return merkle root of the transactions included in the
        block"""
        merkle_root = calculate_hash(self.block_txn_ids)
        return Result.ok(data=merkle_root.encode('utf-8'))
