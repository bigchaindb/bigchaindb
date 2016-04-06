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
        raise NotImplementedError

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
        raise NotImplementedError

    @abstractmethod
    def create_transaction(*args, **kwargs):
        """Create a new transaction.

        Args:
            The signature of this method is left to plugin authors to decide.

        Returns:
            dict: newly constructed transaction.
        """
        raise NotImplementedError

    @abstractmethod
    def sign_transaction(transaction, *args, **kwargs):
        """Sign a transaction.

        Args:
            transaction (dict): transaction to sign.
            any other arguments are left to plugin authors to decide.

        Returns:
            dict: transaction with any signatures applied.
        """
        raise NotImplementedError

    @abstractmethod
    def verify_signature(signed_transaction):
        """Verify the signature of a transaction.

        Args:
            signed_transaction (dict): signed transaction to verify

        Returns:
            bool: True if the transaction's required signature data is present
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
            if transaction['transaction']['inputs']:
                raise ValueError('A CREATE operation has no inputs')
            if transaction['transaction']['current_owner'] not in (
                    bigchain.federation_nodes + [bigchain.me]):
                raise exceptions.OperationError(
                    'Only federation nodes can use the operation `CREATE`')

        else:
            # check if the input exists, is owned by the current_owner
            if not transaction['transaction']['inputs']:
                raise ValueError(
                    'Only `CREATE` transactions can have null inputs')

            # check inputs
            for inp in transaction['transaction']['inputs']:
                tx_input = bigchain.get_transaction(inp)

                if not tx_input:
                    raise exceptions.TransactionDoesNotExist(
                        'input `{}` does not exist in the bigchain'.format(
                            transaction['transaction']['input']))

                if (tx_input['transaction']['new_owner'] !=
                    transaction['transaction']['current_owner']):
                    raise exceptions.TransactionOwnerError(
                        'current_owner `{}` does not own the input `{}`'.format(
                            transaction['transaction']['current_owner'],
                            transaction['transaction']['input']))

                # check if the input was already spent by a transaction other than
                # this one.
                spent = bigchain.get_spent(tx_input['id'])
                if spent and spent['id'] != transaction['id']:
                    raise exceptions.DoubleSpend(
                        'input `{}` was already spent'.format(inp))

        # Check hash of the transaction
        calculated_hash = crypto.hash_data(util.serialize(
            transaction['transaction']))
        if calculated_hash != transaction['id']:
            raise exceptions.InvalidHash()

        # Check signature
        if not util.verify_signature(transaction):
            raise exceptions.InvalidSignature()

        return transaction

    # TODO: Unsure if a bigchain parameter is really necessary here?
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
    def verify_signature(signed_transaction):
        """Verify the signature of a transaction.

        Refer to the documentation of ``bigchaindb.util.verify_signature``
        """

        return util.verify_signature(signed_transaction)
