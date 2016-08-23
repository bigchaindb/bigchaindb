from functools import reduce
from operator import and_

from bigchaindb_common.transaction import Transaction
from bigchaindb_common.exceptions import DoubleSpend, InvalidSignature


class Transaction(Transaction):
    # TODO: Check this against `validate_transaction` again, especially
    #       the hash checking
    def is_valid(self, bigchain):
        inputs_defined = reduce(and_, [ffill.tx_input.is_defined() for ffill
                                       in self.fulfillments])
        if self.operation in (Transaction.CREATE, Transaction.GENESIS):
            if inputs_defined:
                raise ValueError('A CREATE operation has no inputs')
            elif self.operation == Transaction.TRANSFER:

                if len(self.fulfillments) == 0:
                    raise ValueError('Transaction contains no fulfillments')

                if not inputs_defined:
                    raise ValueError('Only `CREATE` transactions can have null inputs')
                for ffill in self.fulfillments:
                    # NOTE: `get_transaction` throws `TransactionDoesNotExist`
                    #       if a transaction with a bespoke id doesn't exist.
                    input_txid = ffill.tx_input.tx_id
                    bigchain.get_transaction(input_txid)

                    # TODO: check if current owners own tx_input (maybe checked
                    #       by InvalidSignature) check if the input was already
                    #       spent by a transaction other than this one.
                    spent = bigchain.get_spent(input_txid, ffill.tx_input.cid)
                    if spent and spent.id != self.id:
                        raise DoubleSpend('input `{}` was already spent'
                                          .format(input_txid))

                # TODO: Validate the hash somehow
                if not self.fulfillments_valid():
                    raise InvalidSignature()
                else:
                    return self
        else:
            raise TypeError('`operation` must be either `TRANSFER`, `CREATE` or `GENESIS`')
