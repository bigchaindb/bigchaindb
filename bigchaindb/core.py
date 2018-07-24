"""This module contains all the goodness to integrate BigchainDB
with Tendermint."""
import logging

from abci.application import BaseApplication
from abci.types_pb2 import (
    ResponseInitChain,
    ResponseInfo,
    ResponseCheckTx,
    ResponseBeginBlock,
    ResponseDeliverTx,
    ResponseEndBlock,
    ResponseCommit,
    Validator,
    PubKey
)

from bigchaindb import BigchainDB
from bigchaindb.tendermint_utils import (decode_transaction,
                                         calculate_hash)
from bigchaindb.lib import Block, PreCommitState
from bigchaindb.backend.query import PRE_COMMIT_ID


CodeTypeOk = 0
CodeTypeError = 1
logger = logging.getLogger(__name__)


class App(BaseApplication):
    """Bridge between BigchainDB and Tendermint.

    The role of this class is to expose the BigchainDB
    transactional logic to the Tendermint Consensus
    State Machine."""

    def __init__(self, bigchaindb=None):
        self.bigchaindb = bigchaindb or BigchainDB()
        self.block_txn_ids = []
        self.block_txn_hash = ''
        self.block_transactions = []
        self.validators = None
        self.new_height = None

    def init_chain(self, validators):
        """Initialize chain with block of height 0"""

        block = Block(app_hash='', height=0, transactions=[])
        self.bigchaindb.store_block(block._asdict())
        return ResponseInitChain()

    def info(self, request):
        """Return height of the latest committed block."""
        r = ResponseInfo()
        block = self.bigchaindb.get_latest_block()
        if block:
            r.last_block_height = block['height']
            r.last_block_app_hash = block['app_hash'].encode('utf-8')
        else:
            r.last_block_height = 0
            r.last_block_app_hash = b''
        return r

    def check_tx(self, raw_transaction):
        """Validate the transaction before entry into
        the mempool.

        Args:
            raw_tx: a raw string (in bytes) transaction."""

        logger.benchmark('CHECK_TX_INIT')
        logger.debug('check_tx: %s', raw_transaction)
        transaction = decode_transaction(raw_transaction)
        if self.bigchaindb.is_valid_transaction(transaction):
            logger.debug('check_tx: VALID')
            logger.benchmark('CHECK_TX_END, tx_id:%s', transaction['id'])
            return ResponseCheckTx(code=CodeTypeOk)
        else:
            logger.debug('check_tx: INVALID')
            logger.benchmark('CHECK_TX_END, tx_id:%s', transaction['id'])
            return ResponseCheckTx(code=CodeTypeError)

    def begin_block(self, req_begin_block):
        """Initialize list of transaction.
        Args:
            req_begin_block: block object which contains block header
            and block hash.
        """
        logger.benchmark('BEGIN BLOCK, height:%s, num_txs:%s',
                         req_begin_block.header.height,
                         req_begin_block.header.num_txs)

        self.block_txn_ids = []
        self.block_transactions = []
        return ResponseBeginBlock()

    def deliver_tx(self, raw_transaction):
        """Validate the transaction before mutating the state.

        Args:
            raw_tx: a raw string (in bytes) transaction."""
        logger.debug('deliver_tx: %s', raw_transaction)
        transaction = self.bigchaindb.is_valid_transaction(
            decode_transaction(raw_transaction), self.block_transactions)

        if not transaction:
            logger.debug('deliver_tx: INVALID')
            return ResponseDeliverTx(code=CodeTypeError)
        else:
            logger.debug('storing tx')
            self.block_txn_ids.append(transaction.id)
            self.block_transactions.append(transaction)
            return ResponseDeliverTx(code=CodeTypeOk)

    def end_block(self, request_end_block):
        """Calculate block hash using transaction ids and previous block
        hash to be stored in the next block.

        Args:
            height (int): new height of the chain."""

        height = request_end_block.height
        self.new_height = height
        block_txn_hash = calculate_hash(self.block_txn_ids)
        block = self.bigchaindb.get_latest_block()

        if self.block_txn_ids:
            self.block_txn_hash = calculate_hash([block['app_hash'], block_txn_hash])
        else:
            self.block_txn_hash = block['app_hash']

        validator_updates = self.bigchaindb.get_validator_update()
        validator_updates = [encode_validator(v) for v in validator_updates]

        # set sync status to true
        self.bigchaindb.delete_validator_update()

        # Store pre-commit state to recover in case there is a crash
        # during `commit`
        pre_commit_state = PreCommitState(commit_id=PRE_COMMIT_ID,
                                          height=self.new_height,
                                          transactions=self.block_txn_ids)
        logger.debug('Updating PreCommitState: %s', self.new_height)
        self.bigchaindb.store_pre_commit_state(pre_commit_state._asdict())
        return ResponseEndBlock(validator_updates=validator_updates)

    def commit(self):
        """Store the new height and along with block hash."""

        data = self.block_txn_hash.encode('utf-8')

        # register a new block only when new transactions are received
        if self.block_txn_ids:
            self.bigchaindb.store_bulk_transactions(self.block_transactions)
            block = Block(app_hash=self.block_txn_hash,
                          height=self.new_height,
                          transactions=self.block_txn_ids)
            # NOTE: storing the block should be the last operation during commit
            # this effects crash recovery. Refer BEP#8 for details
            self.bigchaindb.store_block(block._asdict())

        logger.debug('Commit-ing new block with hash: apphash=%s ,'
                     'height=%s, txn ids=%s', data, self.new_height,
                     self.block_txn_ids)
        logger.benchmark('COMMIT_BLOCK, height:%s', self.new_height)
        return ResponseCommit(data=data)


def encode_validator(v):
    ed25519_public_key = v['pub_key']['data']
    # NOTE: tendermint expects public to be encoded in go-amino format

    pub_key = PubKey(type='ed25519',
                     data=bytes.fromhex(ed25519_public_key))

    return Validator(pub_key=pub_key,
                     address=b'',
                     power=v['power'])
