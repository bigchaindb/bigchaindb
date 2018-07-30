from bigchaindb.common.exceptions import (InvalidSignature,
                                          MultipleInputsError,
                                          InvalidProposer,
                                          UnequalValidatorSet,
                                          InvalidPowerChange,
                                          DuplicateTransaction)
from bigchaindb.tendermint_utils import key_from_base64
from bigchaindb.common.crypto import (public_key_from_ed25519_key)
from bigchaindb.common.transaction import Transaction
from bigchaindb.common.schema import (_validate_schema,
                                      TX_SCHEMA_VALIDATOR_ELECTION,
                                      TX_SCHEMA_COMMON,
                                      TX_SCHEMA_CREATE)


class ValidatorElection(Transaction):

    VALIDATOR_ELECTION = 'VALIDATOR_ELECTION'
    # NOTE: this transaction class extends create so the operation inheritence is achieved
    # by renaming CREATE to VALIDATOR_ELECTION
    CREATE = VALIDATOR_ELECTION
    ALLOWED_OPERATIONS = (VALIDATOR_ELECTION,)

    def __init__(self, operation, asset, inputs, outputs,
                 metadata=None, version=None, hash_id=None):
        # operation `CREATE` is being passed as argument as `VALIDATOR_ELECTION` is an extension
        # of `CREATE` and any validation on `CREATE` in the parent class should apply to it
        super().__init__(operation, asset, inputs, outputs, metadata, version, hash_id)

    @classmethod
    def current_validators(cls, bigchain):
        """Return a dictionary of validators with key as `public_key` and
           value as the `voting_power`
        """

        validators = {}
        for validator in bigchain.get_validators():
            # NOTE: we assume that Tendermint encodes public key in base64
            public_key = public_key_from_ed25519_key(key_from_base64(validator['pub_key']['value']))
            validators[public_key] = validator['voting_power']

        return validators

    @classmethod
    def recipients(cls, bigchain):
        """Convert validator dictionary to a recipient list for `Transaction`"""

        recipients = []
        for public_key, voting_power in cls.current_validators(bigchain).items():
            recipients.append(([public_key], voting_power))

        return recipients

    @classmethod
    def is_same_topology(cls, current_topology, election_topology):
        voters = {}
        for voter in election_topology:
            if len(voter.public_keys) > 1:
                return False

            [public_key] = voter.public_keys
            voting_power = voter.amount
            voters[public_key] = voting_power

        # Check whether the voters and their votes is same to that of the
        # validators and their voting power in the network
        return (current_topology == voters)

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
            `True` if the election is valid

        Raises:
            ValidationError: If the election is invalid
        """
        input_conditions = []

        duplicates = any(txn for txn in current_transactions if txn.id == self.id)
        if bigchain.get_transaction(self.id) or duplicates:
            raise DuplicateTransaction('transaction `{}` already exists'
                                       .format(self.id))

        if not self.inputs_valid(input_conditions):
            raise InvalidSignature('Transaction signature is invalid.')

        current_validators = self.current_validators(bigchain)

        # NOTE: Proposer should be a single node
        if len(self.inputs) != 1 or len(self.inputs[0].owners_before) != 1:
            raise MultipleInputsError('`tx_signers` must be a list instance of length one')

        # NOTE: change more than 1/3 of the current power is not allowed
        if self.asset['data']['power'] >= (1/3)*sum(current_validators.values()):
            raise InvalidPowerChange('`power` change must be less than 1/3 of total power')

        # NOTE: Check if the proposer is a validator.
        [election_initiator_node_pub_key] = self.inputs[0].owners_before
        if election_initiator_node_pub_key not in current_validators.keys():
            raise InvalidProposer('Public key is not a part of the validator set')

        # NOTE: Check if all validators have been assigned votes equal to their voting power
        if not self.is_same_topology(current_validators, self.outputs):
            raise UnequalValidatorSet('Validator set much be exactly same to the outputs of election')

        return True

    @classmethod
    def generate(cls, initiator, voters, election_data, metadata=None):
        (inputs, outputs) = cls.validate_create(initiator, voters, election_data, metadata)
        election = cls(cls.VALIDATOR_ELECTION, {'data': election_data}, inputs, outputs, metadata)
        cls.validate_schema(election.to_dict(), skip_id=True)
        return election

    @classmethod
    def validate_schema(cls, tx, skip_id=False):
        """Validate the validator election transaction. Since `VALIDATOR_ELECTION` extends `CREATE`
           transaction, all the validations for `CREATE` transaction should be inherited
        """
        if not skip_id:
            cls.validate_id(tx)
        _validate_schema(TX_SCHEMA_COMMON, tx)
        _validate_schema(TX_SCHEMA_CREATE, tx)
        _validate_schema(TX_SCHEMA_VALIDATOR_ELECTION, tx)

    @classmethod
    def create(cls, tx_signers, recipients, metadata=None, asset=None):
        raise NotImplementedError

    @classmethod
    def transfer(cls, tx_signers, recipients, metadata=None, asset=None):
        raise NotImplementedError
