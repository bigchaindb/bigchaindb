from bigchaindb.consensus import BaseConsensusRules
from bigchaindb.common import crypto
from bigchaindb.common.util import serialize


def test_verify_vote_passes(b, structurally_valid_vote):
    vote_body = structurally_valid_vote['vote']
    vote_data = serialize(vote_body)
    signature = crypto.PrivateKey(b.me_private).sign(vote_data.encode())
    vote_signed = {
        'node_pubkey': b.me,
        'signature': signature.decode(),
        'vote': vote_body
    }
    assert BaseConsensusRules.verify_vote([b.me], vote_signed)


def test_verify_vote_fails_signature(b, structurally_valid_vote):
    vote_body = structurally_valid_vote['vote']
    vote_signed = {
        'node_pubkey': b.me,
        'signature': 'a' * 86,
        'vote': vote_body
    }
    assert not BaseConsensusRules.verify_vote([b.me], vote_signed)


def test_verify_vote_fails_schema(b):
    vote_body = {}
    vote_data = serialize(vote_body)
    signature = crypto.PrivateKey(b.me_private).sign(vote_data.encode())
    vote_signed = {
        'node_pubkey': b.me,
        'signature': signature.decode(),
        'vote': vote_body
    }
    assert not BaseConsensusRules.verify_vote([b.me], vote_signed)
