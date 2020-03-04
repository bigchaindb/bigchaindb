# Copyright © 2020 Interplanetary Database Association e.V.,
# BigchainDB and IPDB software contributors.
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

from bigchaindb.common.transaction import Transaction
from bigchaindb.common.schema import (_validate_schema,
                                      TX_SCHEMA_COMMON,
                                      TX_SCHEMA_TRANSFER,
                                      TX_SCHEMA_VOTE)


class Vote(Transaction):

    OPERATION = 'VOTE'
    # NOTE: This class inherits TRANSFER txn type. The `TRANSFER` property is
    # overriden to re-use methods from parent class
    TRANSFER = OPERATION
    ALLOWED_OPERATIONS = (OPERATION,)
    # Custom validation schema
    TX_SCHEMA_CUSTOM = TX_SCHEMA_VOTE

    def validate(self, bigchain, current_transactions=[]):
        """Validate election vote transaction
        NOTE: There are no additional validity conditions on casting votes i.e.
        a vote is just a valid TRANFER transaction

        For more details refer BEP-21: https://github.com/bigchaindb/BEPs/tree/master/21

        Args:
            bigchain (BigchainDB): an instantiated bigchaindb.lib.BigchainDB object.

        Returns:
            Vote: a Vote object

        Raises:
            ValidationError: If the election vote is invalid
        """
        self.validate_transfer_inputs(bigchain, current_transactions)
        return self

    @classmethod
    def generate(cls, inputs, recipients, election_id, metadata=None):
        (inputs, outputs) = cls.validate_transfer(inputs, recipients, election_id, metadata)
        election_vote = cls(cls.OPERATION, {'id': election_id}, inputs, outputs, metadata)
        cls.validate_schema(election_vote.to_dict())
        return election_vote

    @classmethod
    def validate_schema(cls, tx):
        """Validate the validator election vote transaction. Since `VOTE` extends `TRANSFER`
           transaction, all the validations for `CREATE` transaction should be inherited
        """
        _validate_schema(TX_SCHEMA_COMMON, tx)
        _validate_schema(TX_SCHEMA_TRANSFER, tx)
        _validate_schema(cls.TX_SCHEMA_CUSTOM, tx)

    @classmethod
    def create(cls, tx_signers, recipients, metadata=None, asset=None):
        raise NotImplementedError

    @classmethod
    def transfer(cls, tx_signers, recipients, metadata=None, asset=None):
        raise NotImplementedError
