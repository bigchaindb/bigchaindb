import base58

from bigchaindb.common.transaction import Transaction
from bigchaindb.common.schema import (_validate_schema,
                                      TX_SCHEMA_COMMON,
                                      TX_SCHEMA_TRANSFER,
                                      TX_SCHEMA_VALIDATOR_ELECTION_VOTE)


class ValidatorElectionVote(Transaction):

    VALIDATOR_ELECTION_VOTE = 'VALIDATOR_ELECTION_VOTE'
    # NOTE: this transaction class extends create so the operation inheritence is achieved
    # by renaming CREATE to VALIDATOR_ELECTION
    TRANSFER = VALIDATOR_ELECTION_VOTE
    ALLOWED_OPERATIONS = (VALIDATOR_ELECTION_VOTE,)

    def __init__(self, operation, asset, inputs, outputs,
                 metadata=None, version=None, hash_id=None):
        # operation `CREATE` is being passed as argument as `VALIDATOR_ELECTION` is an extension
        # of `CREATE` and any validation on `CREATE` in the parent class should apply to it
        super().__init__(operation, asset, inputs, outputs, metadata, version, hash_id)

    def validate(self, bigchain, current_transactions=[]):
        """Validate election transaction
        For more details refer BEP-21: https://github.com/bigchaindb/BEPs/tree/master/21

        NOTE:
        * A valid election is initiated by an existing validator.

        * A valid election is one where voters are validators and votes are
          alloacted according to the voting power of each validator node.

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
        """Validate the validator election transaction. Since `VALIDATOR_ELECTION` extends `CREATE`
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
