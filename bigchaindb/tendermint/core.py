"""This module contains all the goodness to integrate BigchainDB
with Tendermint."""


from abci import (
    ABCIServer,
    BaseApplication,
    ResponseInfo,
    ResponseQuery,
    Result
)

from .utils import decode_transaction
from .lib import validate_transaction, write_transaction


class App(BaseApplication):
    """Bridge between BigchainDB and Tendermint.

    The role of this class is to expose the BigchainDB
    transactional logic to the Tendermint Consensus
    State Machine."""


    def __init__(self, bigchaindb):
        self.bigchaindb = bigchaindb

    def check_tx(self, raw_transaction):
        """Validate the transaction before entry into
        the mempool.

        Args:
            raw_tx: an encoded transaction."""

        transaction = decode_transaction(raw_transaction)
        if validate_transaction(self.bigchaindb, transaction):
            return Result.ok()
        else:
            return Result.error()

    def deliver_tx(self, raw_transaction):
        """Validate the transaction before mutating the state.

        Args:
            raw_tx: an encoded transaction."""

        transaction = validate_transaction(
                self.bigchaindb,
                decode_transaction(raw_transaction))

        if not transaction:
            return Result.error(log='Invalid transaction')
        else:
            write_transaction(self.bigchaindb, transaction)
            return Result.ok()
