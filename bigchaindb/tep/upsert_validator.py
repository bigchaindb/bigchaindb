import json

from bigchaindb.tep.transactional_election import TransactionalElection
from bigchaindb.tendermint.lib import BigchainDB
from bigchaindb.models import Transaction
from bigchaindb.tendermint.utils import (GO_AMINO_ED25519,
                                         key_from_base64,)
from bigchaindb.common.crypto import (key_pair_from_ed35519_key,
                                      public_key_from_ed35519_key)


class UpsertValidator(TransactionalElection):

    version = '1.0'
    name = 'upsert-validator'

    def __init__(self, bigchain=None):
        if not bigchain:
            bigchain = BigchainDB()

        self.bigchain = bigchain

    def _new_election_object(self, args):
        new_election_object = {
            'type': 'election',
            'name': self.name,
            'version': self.version,
            'args': args
        }
        return new_election_object

    def _recipients(self):
        """Convert validator dictionary to a recipient list for `Transaction`"""

        recipients = []
        for public_key, voting_power in self._validators().items():
            recipients.append(([public_key], voting_power))

        return recipients

    def _validators(self):
        """Return a dictionary of validators with key as `public_key` and
           value as the `voting_power`
        """

        validators = {}
        for validator in self.bigchain.get_validators():
            if validator['pub_key']['type'] == GO_AMINO_ED25519:
                public_key = public_key_from_ed35519_key(key_from_base64(validator['pub_key']['value']))
                validators[public_key] = validator['voting_power']
            else:
                # TODO: use appropriate exception
                raise NotImplementedError

        return validators

    def _get_vote(self, tx_election, public_key):
        """For a given `public_key` return the `input` and `amount` as
           voting power
        """

        for i, tx_input in enumerate(tx_election.to_inputs()):
            if tx_input.owners_before == [public_key] and \
               tx_election.output[i].public_keys == [public_key]:
                return ([tx_input], tx_election.output[i].amount)

        return ([], 0)

    def _is_same_topology(current_topology, election_topology):

        voters = {}
        for voter in election_topology:
            [public_key] = voter.public_keys
            voting_power = voter.amount
            voters[public_key] = voting_power

        # Check whether the voters and their votes is same to that of the
        # validators and their voting power in the network
        return (current_topology.items() == voters.items())

    def _execute_action(self, tx):
        (code, msg) = self.bigchain.write_transaction(tx, 'broadcast_tx_commit')
        return (True if code == 202 else False)

    def propose(self, validator_data, node_key_path):
        validator_public_key = validator_data['pub_key']
        validator_power = validator_data['power']
        validator_node_id = validator_data['node_id']

        node_key = load_node_key(node_key_path)

        args = {
            'public_key': validator_public_key,
            'power': validator_power,
            'node_id': validator_node_id
        }

        tx = Transaction.create([node_key.public_key],
                                self._recipients(),
                                asset=self._new_election_object(args))\
                        .sign([node_key.private_key])
        return self._execute_action(tx)

    def is_valid_proposal(self, tx_election):
        """Check if `tx_election` is a valid election"""
        current_validators = self._validators()

        # Check if the `owners_before` public key is a part of the validator set
        [election_initiator_node_pub_key] = tx_election.inputs[0].owners_before
        if election_initiator_node_pub_key not in current_validators.keys():
            return False

        # Check if all outputs are part of the validator set
        return self._is_same_topology(current_validators, tx_election.outputs)

    def vote(self, election_id, node_key_path):
        """Vote on the given `election_id`"""

        tx_election = self.bigchain.get_transaction(election_id)
        node_key = load_node_key(node_key_path)
        (tx_vote_input,
         voting_power) = self._get_vote(tx_election, node_key.public_key)

        tx_vote = Transaction.transfer(tx_vote_input,
                                       [([election_id], voting_power)],
                                       metadata={'type': 'vote'},
                                       asset_id=tx_election.id)\
                             .sign([node_key.private_key])
        return self._execute_action(tx_vote)

    def is_valid_vote(self, tx_vote):
        """Validate casted vote.

           NOTE: We don't need to check the amount of votes since the same has been validated when
           the election was initiated
        """

        if not (isinstance(tx_vote.metadata, dict) and
                tx_vote.metadata.get('type', None) == 'vote'):
            return False

        validators = self._validators().keys()
        [input_vote_owner] = tx_vote.inputs[0].owners_before

        # If the voter is no longer a part of the validator set then return
        if input_vote_owner not in validators:
            return False

        return True

    def is_concluded(self, election_id, current_votes=[]):
        """Check if the Election with `election_id` has gained majority vote"""

        tx_election = self.bigchain.get_transaction(election_id)
        current_validators = self._validators()
        # Check if network topology is exactly same to when the election was initiated
        if not self._is_same_topology(current_validators, tx_election.outputs):
            return (False, None)

        total_votes = sum(current_validators.values())
        votes = 0
        #  Aggregate vote count for `election_id`
        for output in tx_election.outputs:
            vote = self.bigchain.get_spent(election_id, output.to_dict(), current_votes)
            if vote:
                votes = votes + vote.outputs[0].amount

        # Check if >2/3 of total votes have been casted
        if votes > (2/3)*total_votes:
            return (True, tx_election.asset['data'])

        return (False, None)


# Load Tendermint's public and private key from the file path
def load_node_key(path):
    with open(path) as json_data:
        priv_validator = json.load(json_data)
        priv_key = priv_validator['priv_key']['value']
        hex_private_key = key_from_base64(priv_key)
        return key_pair_from_ed35519_key(hex_private_key)
