"""This module contains all the goodness to integrate BigchainDB
with Tendermint."""

from abci import BaseApplication, Result
from abci.types_pb2 import ResponseEndBlock, ResponseInfo

from bigchaindb.tendermint import BigchainDB
from bigchaindb.tendermint.utils import decode_transaction, calculate_hash
from bigchaindb.tendermint.lib import Block


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
        self.block_txn_hash = ''
        self.validators = None
        self.new_height = None

    def init_chain(self, validators):
        """Initialize chain with block of height 0"""

        block = Block(hash='', height=0)
        self.bigchaindb.store_block(block.to_dict())

    def info(self):
        """Return height of the latest committed block."""

        r = ResponseInfo()
        block = self.bigchaindb.get_latest_block()
        if block:
            r.last_block_height = block['height']
            r.last_block_app_hash = block['hash'].encode('utf-8')
        else:
            r.last_block_height = 0
            r.last_block_app_hash = b''
        return r

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
        """Initialize list of transaction."""

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
            self.block_txn_ids.append(transaction.id)
            return Result.ok()

    def end_block(self, height):
        """Calculate block hash using transaction ids and previous block
        hash to be stored in the next block.

        Args:
            height (int): new height of the chain."""

        self.new_height = height
        block_txn_hash = calculate_hash(self.block_txn_ids)
        block = self.bigchaindb.get_latest_block()

        if self.block_txn_ids:
            self.block_txn_hash = calculate_hash([block['hash'], block_txn_hash])
        else:
            self.block_txn_hash = block['hash']

        return ResponseEndBlock()

    def commit(self):
        """Store the new height and along with block hash."""

        # register a new block only when new transactions are received
        if self.block_txn_ids:
            block = Block(hash=self.block_txn_hash, height=self.new_height)
            self.bigchaindb.store_block(block.to_dict())

        data = self.block_txn_hash.encode('utf-8')
        return Result.ok(data=data)
