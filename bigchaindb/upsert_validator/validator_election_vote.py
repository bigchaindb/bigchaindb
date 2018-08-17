# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

import base58

from bigchaindb.common.transaction import Transaction
from bigchaindb.common.schema import (_validate_schema,
                                      TX_SCHEMA_COMMON,
                                      TX_SCHEMA_TRANSFER,
                                      TX_SCHEMA_VALIDATOR_ELECTION_VOTE)


class ValidatorElectionVote(Transaction):

    VALIDATOR_ELECTION_VOTE = 'VALIDATOR_ELECTION_VOTE'
    # NOTE: This class inherits TRANSFER txn type. The `TRANSFER` property is
    # overriden to re-use methods from parent class
    TRANSFER = VALIDATOR_ELECTION_VOTE
    ALLOWED_OPERATIONS = (VALIDATOR_ELECTION_VOTE,)

    def validate(self, bigchain, current_transactions=[]):
        """Validate election vote transaction
        NOTE: There are no additional validity conditions on casting votes i.e.
        a vote is just a valid TRANFER transaction

        For more details refer BEP-21: https://github.com/bigchaindb/BEPs/tree/master/21

        Args:
            bigchain (BigchainDB): an instantiated bigchaindb.lib.BigchainDB object.

        Returns:
            `True` if the election vote is valid

        Raises:
            ValidationError: If the election vote is invalid
        """
        self.validate_transfer_inputs(bigchain, current_transactions)
        return self

    @classmethod
    def to_public_key(cls, election_id):
        return base58.b58encode(bytes.fromhex(election_id))

    @classmethod
    def generate(cls, inputs, recipients, election_id, metadata=None):
        (inputs, outputs) = cls.validate_transfer(inputs, recipients, election_id, metadata)
        election_vote = cls(cls.VALIDATOR_ELECTION_VOTE, {'id': election_id}, inputs, outputs, metadata)
        cls.validate_schema(election_vote.to_dict(), skip_id=True)
        return election_vote

    @classmethod
    def validate_schema(cls, tx, skip_id=False):
        """Validate the validator election vote transaction. Since `VALIDATOR_ELECTION_VOTE` extends `TRANFER`
           transaction, all the validations for `CREATE` transaction should be inherited
        """
        if not skip_id:
            cls.validate_id(tx)
        _validate_schema(TX_SCHEMA_COMMON, tx)
        _validate_schema(TX_SCHEMA_TRANSFER, tx)
        _validate_schema(TX_SCHEMA_VALIDATOR_ELECTION_VOTE, tx)

    @classmethod
    def create(cls, tx_signers, recipients, metadata=None, asset=None):
        raise NotImplementedError

    @classmethod
    def transfer(cls, tx_signers, recipients, metadata=None, asset=None):
        raise NotImplementedError
