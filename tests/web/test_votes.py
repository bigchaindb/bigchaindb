import pytest

from bigchaindb.models import Transaction

VOTES_ENDPOINT = '/api/v1/votes'


@pytest.mark.bdb
@pytest.mark.usefixtures('inputs')
def test_get_votes_endpoint(b, client):
    tx = Transaction.create([b.me], [([b.me], 1)])
    tx = tx.sign([b.me_private])

    block = b.create_block([tx])
    b.write_block(block)

    # vote the block valid
    vote = b.vote(block.id, b.get_last_voted_block().id, True)
    b.write_vote(vote)

    res = client.get(VOTES_ENDPOINT + "?block_id=" + block.id)
    assert vote == res.json[0]
    assert len(res.json) == 1
    assert res.status_code == 200


@pytest.mark.bdb
@pytest.mark.usefixtures('inputs')
def test_get_votes_multiple(b, client):
    tx = Transaction.create([b.me], [([b.me], 1)])
    tx = tx.sign([b.me_private])

    block = b.create_block([tx])
    b.write_block(block)
    last_block = b.get_last_voted_block().id
    # vote the block valid
    vote_valid = b.vote(block.id, last_block, True)
    b.write_vote(vote_valid)

    # vote the block valid
    vote_invalid = b.vote(block.id, last_block, False)
    b.write_vote(vote_invalid)

    res = client.get(VOTES_ENDPOINT + "?block_id=" + block.id)
    assert len(res.json) == 2
    assert res.status_code == 200


@pytest.mark.bdb
def test_get_votes_endpoint_returns_empty_list_not_found(client):
    res = client.get(VOTES_ENDPOINT + "?block_id=123")
    assert [] == res.json
    assert res.status_code == 200


@pytest.mark.bdb
def test_get_status_endpoint_returns_400_bad_query_params(client):
    res = client.get(VOTES_ENDPOINT)
    assert res.status_code == 400

    res = client.get(VOTES_ENDPOINT + "?ts_id=123")
    assert res.status_code == 400

    res = client.get(VOTES_ENDPOINT + "?tx_id=123&block_id=123")
    assert res.status_code == 400
