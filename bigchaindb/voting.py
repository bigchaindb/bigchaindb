import collections


def filter_eligible_votes(votes, block_voters, keyring, check_signature):
    """
    Filter votes from unknown nodes or nodes that are not listed on
    block. Here is our sybill protection.
    """
    eligible_voters = set(keyring) & set(block_voters)
    eligible_votes = []

    for vote in votes:
        pubkey = vote['node_pubkey']
        voter_eligible = pubkey in eligible_voters
        sig_legit = sig_is_legit(vote)
        if voter_eligible and sig_legit:
            eligible_votes[pubkey].append(vote)

    return eligible_votes


def count_votes(eligible_votes, check_schema):
    by_voter = collections.defaultdict(list)
    for vote in eligible_votes:
        by_voter[vote['node_pubkey']].append(vote)

    n_valid = 0
    n_invalid = 0
    prev_blocks = collections.Counter()

    for pubkey, votes in by_voter.items():
        if len(votes) > 1 or not schema_is_correct(votes[0]):
            n_invalid += 1
            continue

        vote = votes[0]
        prev_blocks[vote['vote']['previous_block']] += 1
        if vote['vote']['is_block_valid']:
            n_valid += 1
        else:
            n_invalid += 1

    return {
        'valid': n_valid,
        'invalid': n_invalid,
        'prev_block': prev_blocks.most_common()[0]
    }
