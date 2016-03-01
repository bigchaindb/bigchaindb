# TODO: no real reason to use abc yet, but later we can enforce inheritance from
#       this class when loading plugins if that's desirable.
# from abc import ABCMeta

class AbstractConsensusRules:

    # TODO: rather than having plugin-authors inherit and override,
    #       it'd be cleaner to make a `transactionrule` decorator and etc
    @classmethod
    def validate_transaction(cls, bigchain, transaction):
        """Validate a transaction.

        Args:
            bigchain (Bigchain): an instantiated bigchaindb.Bigchain object.
            transaction (dict): transaction to validate.

        Returns:
            The transaction if the transaction is valid else it raises an
            exception describing the reason why the transaction is invalid.

        Raises:
            Descriptive exceptions indicating the reason the transaction failed.
            See the `exceptions` module for bigchain-native error classes.
        """
        return transaction

    @classmethod
    def validate_block(cls, bigchain, block):
        """Validate a block.

        Args:
            bigchain (Bigchain): an instantiated bigchaindb.Bigchain object.
            block (dict): block to validate.

        Returns:
            The block if the block is valid else it raises and exception
            describing the reason why the block is invalid.

        Raises:
            Descriptive exceptions indicating the reason the block failed.
            See the `exceptions` module for bigchain-native error classes.
        """
        return block
