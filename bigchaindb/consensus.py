import copy
from abc import ABCMeta, abstractmethod

import bigchaindb.exceptions as exceptions
from bigchaindb import util
from bigchaindb import crypto


class AbstractConsensusRules(metaclass=ABCMeta):
    """Abstract base class for Bigchain plugins which implement consensus logic.

    A consensus plugin must expose a class inheriting from this one via an
    entry_point.

    All methods listed below must be implemented.
    """

    @staticmethod
    @abstractmethod
    def validate_transaction(bigchain, transaction):
        """Validate a transaction.

        Args:
            bigchain (Bigchain): an instantiated ``bigchaindb.Bigchain`` object.
            transaction (dict): transaction to validate.

        Returns:
            The transaction if the transaction is valid else it raises an
            exception describing the reason why the transaction is invalid.

        Raises:
            Descriptive exceptions indicating the reason the transaction failed.
            See the `exceptions` module for bigchain-native error classes.
        """

    @staticmethod
    @abstractmethod
    def validate_block(bigchain, block):
        """Validate a block.

        Args:
            bigchain (Bigchain): an instantiated ``bigchaindb.Bigchain`` object.
            block (dict): block to validate.

        Returns:
            The block if the block is valid else it raises an exception
            describing the reason why the block is invalid.

        Raises:
            Descriptive exceptions indicating the reason the block failed.
            See the `exceptions` module for bigchain-native error classes.
        """

    @staticmethod
    @abstractmethod
    def create_transaction(*args, **kwargs):
        """Create a new transaction.

        Args:
            The signature of this method is left to plugin authors to decide.

        Returns:
            dict: newly constructed transaction.
        """

    @staticmethod
    @abstractmethod
    def sign_transaction(transaction, *args, **kwargs):
        """Sign a transaction.

        Args:
            transaction (dict): transaction to sign.
            any other arguments are left to plugin authors to decide.

        Returns:
            dict: transaction with any signatures applied.
        """

    @staticmethod
    @abstractmethod
    def validate_fulfillments(signed_transaction):
        """Validate the fulfillments of a transaction.

        Args:
            signed_transaction (dict): signed transaction to verify

        Returns:
            bool: True if the transaction's required fulfillments are present
                and correct, False otherwise.
        """

    @abstractmethod
    def verify_vote_signature(block, signed_vote):
        """Verify a cast vote.

        Args:
            block (dict): block under election
            signed_vote (dict): signed vote to verify

        Returns:
            bool: True if the votes's required signature data is present
                and correct, False otherwise.
        """
        raise NotImplementedError

class BaseConsensusRules(AbstractConsensusRules):
    """Base consensus rules for Bigchain.

    This class can be copied or overridden to write your own consensus rules!
    """

    @staticmethod
    def validate_transaction(bigchain, transaction):
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

        # If the operation is CREATE the transaction should have no inputs and
        # should be signed by a federation node
        if transaction['transaction']['operation'] == 'CREATE':
            # TODO: for now lets assume a CREATE transaction only has one fulfillment
            if transaction['transaction']['fulfillments'][0]['input']:
                raise ValueError('A CREATE operation has no inputs')
            # TODO: for now lets assume a CREATE transaction only has one current_owner
            if transaction['transaction']['fulfillments'][0]['current_owners'][0] not in (
                    bigchain.nodes_except_me + [bigchain.me]):
                raise exceptions.OperationError(
                    'Only federation nodes can use the operation `CREATE`')

        else:
            # check if the input exists, is owned by the current_owner
            if not transaction['transaction']['fulfillments']:
                raise ValueError('Transaction contains no fulfillments')

            # check inputs
            for fulfillment in transaction['transaction']['fulfillments']:
                if not fulfillment['input']:
                    raise ValueError('Only `CREATE` transactions can have null inputs')
                tx_input = bigchain.get_transaction(fulfillment['input']['txid'])

                if not tx_input:
                    raise exceptions.TransactionDoesNotExist(
                        'input `{}` does not exist in the bigchain'.format(
                            fulfillment['input']['txid']))
                # TODO: check if current owners own tx_input (maybe checked by InvalidSignature)
                # check if the input was already spent by a transaction other than
                # this one.
                spent = bigchain.get_spent(fulfillment['input'])
                if spent and spent['id'] != transaction['id']:
                    raise exceptions.DoubleSpend(
                        'input `{}` was already spent'.format(fulfillment['input']))

        # Check hash of the transaction
        calculated_hash = util.get_hash_data(transaction)
        if calculated_hash != transaction['id']:
            raise exceptions.InvalidHash()

        # Check fulfillments
        if not util.validate_fulfillments(transaction):
            raise exceptions.InvalidSignature()

        return transaction

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
        calculated_hash = crypto.hash_data(util.serialize(block['block']))
        if calculated_hash != block['id']:
            raise exceptions.InvalidHash()

        # Check if the block was created by a federation node
        if block['block']['node_pubkey'] not in (bigchain.nodes_except_me + [bigchain.me]):
            raise exceptions.OperationError('Only federation nodes can create blocks')

        # Check if block signature is valid
        verifying_key = crypto.VerifyingKey(block['block']['node_pubkey'])
        if not verifying_key.verify(util.serialize(block['block']), block['signature']):
            raise exceptions.InvalidSignature('Invalid block signature')

        return block

    @staticmethod
    def create_transaction(current_owner, new_owner, tx_input, operation,
                           payload=None):
        """Create a new transaction

        Refer to the documentation of ``bigchaindb.util.create_tx``
        """

        return util.create_tx(current_owner, new_owner, tx_input, operation,
                              payload)

    @staticmethod
    def sign_transaction(transaction, private_key):
        """Sign a transaction

        Refer to the documentation of ``bigchaindb.util.sign_tx``
        """

        return util.sign_tx(transaction, private_key)

    @staticmethod
    def validate_fulfillments(signed_transaction):
        """Validate the fulfillments of a transaction.

        Refer to the documentation of ``bigchaindb.util.validate_fulfillments``
        """

        return util.validate_fulfillments(signed_transaction)

    @staticmethod
    def verify_vote_signature(block, signed_vote):
        """Verify the signature of a vote.

        Refer to the documentation of ``bigchaindb.util.verify_signature``
        """

        return util.verify_vote_signature(block, signed_vote)
