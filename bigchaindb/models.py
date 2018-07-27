from bigchaindb.common.exceptions import (InvalidSignature, DoubleSpend,
                                          InputDoesNotExist,
                                          TransactionNotInValidBlock,
                                          AssetIdMismatch, AmountError,
                                          DuplicateTransaction)
from bigchaindb.common.transaction import Transaction
from bigchaindb.common.utils import (validate_txn_obj, validate_key)
from bigchaindb.common.schema import validate_transaction_schema
from bigchaindb.backend.schema import validate_language_key


class Transaction(Transaction):

    def validate(self, bigchain, current_transactions=[]):
        """Validate transaction spend

        Args:
            bigchain (BigchainDB): an instantiated bigchaindb.BigchainDB object.

        Returns:
            The transaction (Transaction) if the transaction is valid else it
            raises an exception describing the reason why the transaction is
            invalid.

        Raises:
            ValidationError: If the transaction is invalid
        """
        input_conditions = []

        if self.operation == Transaction.CREATE:
            duplicates = any(txn for txn in current_transactions if txn.id == self.id)
            if bigchain.get_transaction(self.to_dict()['id']) or duplicates:
                raise DuplicateTransaction('transaction `{}` already exists'
                                           .format(self.id))
        elif self.operation == Transaction.TRANSFER:
            # store the inputs so that we can check if the asset ids match
            input_txs = []
            for input_ in self.inputs:
                input_txid = input_.fulfills.txid
                input_tx, status = bigchain.\
                    get_transaction(input_txid, include_status=True)

                if input_tx is None:
                    for ctxn in current_transactions:
                        # assume that the status as valid for previously validated
                        # transactions in current round
                        if ctxn.id == input_txid:
                            input_tx = ctxn
                            status = bigchain.TX_VALID

                if input_tx is None:
                    raise InputDoesNotExist("input `{}` doesn't exist"
                                            .format(input_txid))

                if status != bigchain.TX_VALID:
                    raise TransactionNotInValidBlock(
                        'input `{}` does not exist in a valid block'.format(
                            input_txid))

                spent = bigchain.get_spent(input_txid, input_.fulfills.output,
                                           current_transactions)
                if spent and spent.id != self.id:
                    raise DoubleSpend('input `{}` was already spent'
                                      .format(input_txid))

                output = input_tx.outputs[input_.fulfills.output]
                input_conditions.append(output)
                input_txs.append(input_tx)

            # Validate that all inputs are distinct
            links = [i.fulfills.to_uri() for i in self.inputs]
            if len(links) != len(set(links)):
                raise DoubleSpend('tx "{}" spends inputs twice'.format(self.id))

            # validate asset id
            asset_id = Transaction.get_asset_id(input_txs)
            if asset_id != self.asset['id']:
                raise AssetIdMismatch(('The asset id of the input does not'
                                       ' match the asset id of the'
                                       ' transaction'))

            input_amount = sum([input_condition.amount for input_condition in input_conditions])
            output_amount = sum([output_condition.amount for output_condition in self.outputs])

            if output_amount != input_amount:
                raise AmountError(('The amount used in the inputs `{}`'
                                   ' needs to be same as the amount used'
                                   ' in the outputs `{}`')
                                  .format(input_amount, output_amount))

        if not self.inputs_valid(input_conditions):
            raise InvalidSignature('Transaction signature is invalid.')

        return self

    @classmethod
    def from_dict(cls, tx_body):
        return super().from_dict(tx_body, False)

    @classmethod
    def validate_schema(cls, tx_body):
        cls.validate_id(tx_body)
        validate_transaction_schema(tx_body)
        validate_txn_obj('asset', tx_body['asset'], 'data', validate_key)
        validate_txn_obj('metadata', tx_body, 'metadata', validate_key)
        validate_language_key(tx_body['asset'], 'data')


class FastTransaction:
    """A minimal wrapper around a transaction dictionary. This is useful for
    when validation is not required but a routine expects something that looks
    like a transaction, for example during block creation.

    Note: immutability could also be provided
    """

    def __init__(self, tx_dict):
        self.data = tx_dict

    @property
    def id(self):
        return self.data['id']

    def to_dict(self):
        return self.data
