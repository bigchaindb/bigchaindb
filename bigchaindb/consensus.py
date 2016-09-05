from functools import reduce
from operator import and_

from bigchaindb_common import crypto, exceptions
from bigchaindb_common.transaction import Transaction

from bigchaindb import util


class BaseConsensusRules():
    """Base consensus rules for Bigchain.

    This class can be copied or overridden to write your own consensus rules!
    """

    @staticmethod
    def validate_transaction(bigchain, transaction):
        # TODO: Update this comment
        """Validate a transaction.

        Args:
            bigchain (Bigchain): an instantiated bigchaindb.Bigchain object.
            transaction (dict): transaction to validate.

        Returns:
            The transaction if the transaction is valid else it raises an
            exception describing the reason why the transaction is invalid.

        Raises:
            OperationError: if the transaction operation is not supported
            TransactionDoesNotExist: if the input of the transaction is not found
            TransactionOwnerError: if the new transaction is using an input it doesn't own
            DoubleSpend: if the transaction is a double spend
            InvalidHash: if the hash of the transaction is wrong
            InvalidSignature: if the signature of the transaction is wrong
        """
        inputs_defined = reduce(and_, [bool(ffill.tx_input) for ffill
                                       in transaction.fulfillments])
        if transaction.operation in (Transaction.CREATE, Transaction.GENESIS):
            if inputs_defined:
                raise ValueError('A CREATE operation has no inputs')
        elif transaction.operation == Transaction.TRANSFER:

            if len(transaction.fulfillments) == 0:
                raise ValueError('Transaction contains no fulfillments')

            if not inputs_defined:
                raise ValueError('Only `CREATE` transactions can have null inputs')

            input_conditions = []
            for ffill in transaction.fulfillments:
                input_txid = ffill.tx_input.txid
                input_cid = ffill.tx_input.cid
                input_tx = bigchain.get_transaction(input_txid)
                if input_tx is None:
                    raise exceptions.TransactionDoesNotExist("input `{}` doesn't exist"
                                                             .format(input_txid))
                else:
                    input_conditions.append(input_tx.conditions[input_cid])

                spent = bigchain.get_spent(input_txid, ffill.tx_input.cid)
                if spent and spent.id != transaction.id:
                    raise exceptions.DoubleSpend('input `{}` was already spent'
                                                 .format(input_txid))

            if not transaction.fulfillments_valid(input_conditions):
                raise exceptions.InvalidSignature()
            else:
                return transaction
        else:
            raise TypeError('`operation` must be either `TRANSFER`, `CREATE` or `GENESIS`')

    @staticmethod
    def validate_block(bigchain, block):
        """Validate a block.

        Args:
            bigchain (Bigchain): an instantiated bigchaindb.Bigchain object.
            block (dict): block to validate.

        Returns:
            The block if the block is valid else it raises an exception
            describing the reason why the block is invalid.

        Raises:
            InvalidHash: if the hash of the block is wrong.
        """

        # Check if current hash is correct
        calculated_hash = crypto.hash_data(util.serialize_block(block['block']))
        if calculated_hash != block['id']:
            raise exceptions.InvalidHash()

        # Check if the block was created by a federation node
        if block['block']['node_pubkey'] not in (bigchain.nodes_except_me + [bigchain.me]):
            raise exceptions.OperationError('Only federation nodes can create blocks')

        # Check if block signature is valid
        verifying_key = crypto.VerifyingKey(block['block']['node_pubkey'])
        if not verifying_key.verify(util.serialize_block(block['block']), block['signature']):
            raise exceptions.InvalidSignature('Invalid block signature')

        return block

    @staticmethod
    def verify_vote_signature(block, signed_vote):
        """Verify the signature of a vote.

        Refer to the documentation of ``bigchaindb.util.verify_signature``
        """

        return util.verify_vote_signature(block, signed_vote)
