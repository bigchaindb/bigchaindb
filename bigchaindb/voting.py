import collections
from bigchaindb.common.schema import SchemaValidationError, validate_vote_schema
from bigchaindb.common.utils import serialize
from bigchaindb.common.crypto import PublicKey


VALID = 'valid'
INVALID = 'invalid'
UNDECIDED = 'undecided'


class Voting:
    """
    Everything to do with creating and checking votes.

    All functions in this class should be referentially transparent, that is,
    they always give the same output for a given input. This makes it easier
    to test. This also means no logging!

    Assumptions regarding data:
        * Vote is a dictionary, but it is not assumed that any properties are.
        * Everything else is assumed to be structurally correct, otherwise errors
        may be thrown.
    """

    @classmethod
    def block_election(cls, block, votes, keyring):
        """
        Calculate the election status of a block.
        """
        eligible_voters = set(block['block']['voters']) & set(keyring)
        eligible_votes, ineligible_votes = \
            cls.partition_eligible_votes(votes, eligible_voters)
        n_voters = len(eligible_voters)
        results = cls.count_votes(eligible_votes)
        results['status'] = cls.decide_votes(n_voters, **results['counts'])
        results['ineligible'] = ineligible_votes
        return results

    @classmethod
    def partition_eligible_votes(cls, votes, eligible_voters):
        """
        Filter votes from unknown nodes or nodes that are not listed on
        block. This is the primary Sybill protection.
        """
        eligible, ineligible = ([], [])

        for vote in votes:
            voter_eligible = vote.get('node_pubkey') in eligible_voters
            if voter_eligible:
                try:
                    cls.verify_vote_signature(vote)
                except ValueError:
                    pass
                else:
                    eligible.append(vote)
                    continue
            ineligible.append(vote)

        return eligible, ineligible

    @classmethod
    def count_votes(cls, eligible_votes):
        """
        Given a list of eligible votes, (votes from known nodes that are listed
        as voters), count the votes to produce three quantities:

            Number of votes that say valid
            Number of votes that say invalid
            Highest agreement on previous block ID

        Also, detect if there are multiple votes from a single node and return them
        in a separate "cheat" dictionary.
        """
        by_voter = collections.defaultdict(list)
        for vote in eligible_votes:
            by_voter[vote['node_pubkey']].append(vote)

        n_valid = 0
        n_invalid = 0
        prev_blocks = collections.Counter()
        cheat = []
        malformed = []

        for pubkey, votes in by_voter.items():
            if len(votes) > 1:
                cheat.append(votes)
                n_invalid += 1
                continue

            vote = votes[0]

            if not cls.verify_vote_schema(vote):
                malformed.append(vote)
                n_invalid += 1
                continue

            prev_blocks[vote['vote']['previous_block']] += 1
            if vote['vote']['is_block_valid']:
                n_valid += 1
            else:
                n_invalid += 1

        n_prev = prev_blocks.most_common()[0][1] if prev_blocks else 0

        return {
            'counts': {
                'n_valid': n_valid,
                'n_invalid': n_invalid,
                'n_agree_prev_block': n_prev,
            },
            'cheat': cheat,
            'malformed': malformed,
        }

    @classmethod
    def decide_votes(cls, n_voters, n_valid, n_invalid, n_agree_prev_block):
        """
        Decide on votes.

        To return VALID there must be a clear majority that say VALID
        and also agree on the previous block. This is achieved using the > operator.

        A tie on an even number of votes counts as INVALID so the >= operator is
        used.
        """

        # Check insane cases. This is basic, not exhaustive.
        if n_valid + n_invalid > n_voters or n_agree_prev_block > n_voters:
            raise ValueError('Arguments not sane: %s' % {
                'n_voters': n_voters,
                'n_valid': n_valid,
                'n_invalid': n_invalid,
                'n_agree_prev_block': n_agree_prev_block,
            })

        if n_invalid * 2 >= n_voters:
            return INVALID
        if n_valid * 2 > n_voters:
            if n_agree_prev_block * 2 > n_voters:
                return VALID
            return INVALID
        return UNDECIDED

    @classmethod
    def verify_vote_signature(cls, vote):
        """Verify the signature of a vote

        A valid vote should have been signed by a voter's private key.

        Args:
            vote (list): voters of the block that is under election

        Returns:
            bool: True if the signature is correct, False otherwise.
        """
        signature = vote.get('signature')
        pk_base58 = vote.get('node_pubkey')

        if not (type(signature) == str and type(pk_base58) == str):
            raise ValueError('Malformed vote: %s' % vote)

        public_key = PublicKey(pk_base58)
        body = serialize(vote['vote']).encode()
        return public_key.verify(body, signature)

    @classmethod
    def verify_vote_schema(cls, vote):
        # I'm not sure this is the correct approach. Maybe we should allow
        # duck typing w/r/t votes.
        try:
            validate_vote_schema(vote)
            return True
        except SchemaValidationError:
            return False
