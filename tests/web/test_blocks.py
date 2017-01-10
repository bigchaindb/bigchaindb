import pytest

from bigchaindb.models import Transaction

BLOCKS_ENDPOINT = '/api/v1/blocks/'


@pytest.mark.bdb
@pytest.mark.usefixtures('inputs')
def test_get_block_endpoint(b, client):
    tx = Transaction.create([b.me], [([b.me], 1)])
    tx = tx.sign([b.me_private])

    block = b.create_block([tx])
    b.write_block(block)

    res = client.get(BLOCKS_ENDPOINT + block.id)
    assert block.to_dict() == res.json
    assert res.status_code == 200


@pytest.mark.bdb
@pytest.mark.usefixtures('inputs')
def test_get_block_returns_404_if_not_found(client):
    res = client.get(BLOCKS_ENDPOINT + '123')
    assert res.status_code == 404

    res = client.get(BLOCKS_ENDPOINT + '123/')
    assert res.status_code == 404


@pytest.mark.bdb
@pytest.mark.usefixtures('inputs')
def test_get_blocks_by_txid_endpoint(b, client):
    tx = Transaction.create([b.me], [([b.me], 1)])
    tx = tx.sign([b.me_private])

    tx2 = Transaction.create([b.me], [([b.me], 10)])
    tx2 = tx2.sign([b.me_private])

    block_invalid = b.create_block([tx])
    b.write_block(block_invalid)

    res = client.get(BLOCKS_ENDPOINT + "?tx_id=" + tx.id)
    # test if block is retrieved as undecided
    assert res.status_code == 200
    assert block_invalid.id in res.json
    assert res.json[block_invalid.id] == b.block_election_status(block_invalid.id, block_invalid.voters)
    assert res.json[block_invalid.id] == 'undecided'
    assert len(res.json) == 1

    # vote the block invalid
    vote = b.vote(block_invalid.id, b.get_last_voted_block().id, False)
    b.write_vote(vote)

    res = client.get(BLOCKS_ENDPOINT + "?tx_id=" + tx.id)
    # test if block is retrieved as invalid
    assert res.status_code == 200
    assert block_invalid.id in res.json
    assert res.json[block_invalid.id] == b.block_election_status(block_invalid.id, block_invalid.voters)
    assert res.json[block_invalid.id] == 'invalid'
    assert len(res.json) == 1

    # create a new block containing the same tx (and tx2 to avoid block id collision)
    block_valid = b.create_block([tx, tx2])
    b.write_block(block_valid)

    res = client.get(BLOCKS_ENDPOINT + "?tx_id=" + tx.id)
    # test if block is retrieved as undecided
    assert res.status_code == 200
    assert block_valid.id in res.json
    assert res.json[block_valid.id] == b.block_election_status(block_valid.id, block_valid.voters)
    assert res.json[block_valid.id] == 'undecided'
    assert len(res.json) == 2

    # vote the block valid
    vote = b.vote(block_valid.id, block_invalid.id, True)
    b.write_vote(vote)

    res = client.get(BLOCKS_ENDPOINT + "?tx_id=" + tx.id)
    # test if block is retrieved as valid
    assert res.status_code == 200
    assert block_valid.id in res.json
    assert res.json[block_valid.id] == b.block_election_status(block_valid.id, block_valid.voters)
    assert res.json[block_valid.id] == 'valid'
    assert len(res.json) == 2


@pytest.mark.bdb
def test_get_blocks_by_txid_endpoint_returns_404_if_not_found(client):
    res = client.get(BLOCKS_ENDPOINT + "?tx_id=123")
    assert res.status_code == 404


@pytest.mark.bdb
def test_get_blocks_by_txid_endpoint_returns_400_bad_query_params(client):
    res = client.get(BLOCKS_ENDPOINT)
    assert res.status_code == 400

    res = client.get(BLOCKS_ENDPOINT + "?ts_id=123")
    assert res.status_code == 400

    res = client.get(BLOCKS_ENDPOINT + "?tx_id=123&block_id=123")
    assert res.status_code == 400
