"""This module contains all the goodness to integrate BigchainDB
with Tendermint."""


from abci import BaseApplication, Result

from bigchaindb.tendermint import BigchainDB
from bigchaindb.tendermint.utils import decode_transaction


class App(BaseApplication):
    """Bridge between BigchainDB and Tendermint.

    The role of this class is to expose the BigchainDB
    transactional logic to the Tendermint Consensus
    State Machine."""

    def __init__(self, bigchaindb=None):
        if not bigchaindb:
            bigchaindb = BigchainDB()
        self.bigchaindb = bigchaindb

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
            return Result.ok()
