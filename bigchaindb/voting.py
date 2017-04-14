import collections

from bigchaindb.common.schema import SchemaValidationError, validate_vote_schema
from bigchaindb.exceptions import CriticalDuplicateVote
from bigchaindb.common.utils import serialize
from bigchaindb.common.crypto import PublicKey


VALID = 'valid'
INVALID = 'invalid'
UNDECIDED = 'undecided'


class Voting:
    """
    Everything to do with verifying and counting votes for block election.

    All functions in this class should be referentially transparent, that is,
    they always give the same output for a given input. This makes it easier
    to test. This also means no logging!

    Assumptions regarding data:
        * Vote is a dictionary, but no assumptions are made on it's properties.
        * Everything else is assumed to be structurally correct, otherwise errors
        may be thrown.
    """

    @classmethod
    def block_election(cls, block, votes, keyring):
        """
        Calculate the election status of a block.
        """
        eligible_voters = set(block['block']['voters']) & set(keyring)
        n_voters = len(eligible_voters)
        eligible_votes, ineligible_votes = \
            cls.partition_eligible_votes(votes, eligible_voters)
        by_voter = cls.dedupe_by_voter(eligible_votes)
        results = cls.count_votes(by_voter)
        results['block_id'] = block['id']
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
                    if cls.verify_vote_signature(vote):
                        eligible.append(vote)
                        continue
                except ValueError:
                    pass
            ineligible.append(vote)
        return eligible, ineligible

    @classmethod
    def dedupe_by_voter(cls, eligible_votes):
        """
        Throw a critical error if there is a duplicate vote
        """
        by_voter = {}
        for vote in eligible_votes:
            pubkey = vote['node_pubkey']
            if pubkey in by_voter:
                raise CriticalDuplicateVote(pubkey)
            by_voter[pubkey] = vote
        return by_voter

    @classmethod
    def count_votes(cls, by_voter):
        """
        Given a list of eligible votes, (votes from known nodes that are listed
        as voters), produce the number that say valid and the number that say
        invalid. Votes must agree on previous block, otherwise they become invalid.
        """
        prev_blocks = collections.Counter()
        malformed = []

        for vote in by_voter.values():
            if not cls.verify_vote_schema(vote):
                malformed.append(vote)
                continue

            if vote['vote']['is_block_valid'] is True:
                prev_blocks[vote['vote']['previous_block']] += 1

        n_valid = 0
        prev_block = None
        # Valid votes must agree on previous block
        if prev_blocks:
            prev_block, n_valid = prev_blocks.most_common()[0]
            del prev_blocks[prev_block]

        return {
            'counts': {
                'n_valid': n_valid,
                'n_invalid': len(by_voter) - n_valid,
            },
            'malformed': malformed,
            'previous_block': prev_block,
            'other_previous_block': dict(prev_blocks),
        }

    @classmethod
    def decide_votes(cls, n_voters, n_valid, n_invalid):
        """
        Decide on votes.

        To return VALID there must be a clear majority that say VALID
        and also agree on the previous block.

        A tie on an even number of votes counts as INVALID.
        """
        if n_invalid * 2 >= n_voters:
            return INVALID
        if n_valid * 2 > n_voters:
            return VALID
        return UNDECIDED

    @classmethod
    def verify_vote_signature(cls, vote):
        """
        Verify the signature of a vote
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
        except SchemaValidationError as e:
            return False
