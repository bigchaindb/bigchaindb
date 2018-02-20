from bigchaindb.models import Transaction
from bigchaindb.voting import Voting


class BaseConsensusRules():
    """Base consensus rules for Bigchain.

    A consensus plugin must expose a class inheriting from this one via an entry_point.

    All methods listed below must be implemented.

    """
    voting = Voting

    @staticmethod
    def validate_transaction(bigchain, transaction):
        """See :meth:`bigchaindb.models.Transaction.validate`
        for documentation."""
        input_txs = None 
 
        result = transaction.validate(bigchain, input_txs) 
 
        if transaction.operation == Transaction.TRANSFER: 
            input_txs = transaction.get_input_txs(bigchain) 
 
            transaction.validate_asset( 
                bigchain, 
                [input_tx 
                 for (input_, input_tx, status) 
                 in input_txs if input_tx is not None]) 
 
            transaction.validate_amount( 
                [input_tx.outputs[input_.fulfills.output] 
                 for (input_, input_tx, status) 
                 in input_txs if input_tx is not None]) 
 
        return result

    @staticmethod
    def validate_block(bigchain, block):
        """See :meth:`bigchaindb.models.Block.validate` for documentation."""
        return block.validate(bigchain)

