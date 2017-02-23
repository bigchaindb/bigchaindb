"""
Everything to do with creating and checking votes.
All functions in this module should be referentially transparent, that is,
they always give the same output for a given input. This makes it easier
to test.
"""
import collections


VALID = 'valid'
INVALID = 'invalid'
UNDECIDED = 'undecided'


def partition_eligible_votes(votes, eligible_voters, verify_vote_signature):
    """
    Filter votes from unknown nodes or nodes that are not listed on
    block. This is the primary Sybill protection.
    """
    eligible, ineligible = ([], [])

    for vote in votes:
        voter_eligible = vote['node_pubkey'] in eligible_voters
        if voter_eligible and verify_vote_signature(vote):
            eligible.append(vote)
        else:
            ineligible.append(vote)

    return eligible, ineligible


def count_votes(eligible_votes):
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
    cheat = {}

    for pubkey, votes in by_voter.items():
        if len(votes) > 1:
            cheat[pubkey] = votes
            n_invalid += 1
            continue

        vote = votes[0]
        prev_blocks[vote['vote']['previous_block']] += 1
        if vote['vote']['is_block_valid']:
            n_valid += 1
        else:
            n_invalid += 1

    return {
        'n_valid': n_valid,
        'n_invalid': n_invalid,
        'n_agree_prev_block': prev_blocks.most_common()[0][1]
    }, cheat


def decide_votes(n_voters, n_valid, n_invalid, n_agree_prev_block):
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
