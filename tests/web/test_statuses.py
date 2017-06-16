import pytest

from bigchaindb.models import Transaction

STATUSES_ENDPOINT = '/api/v1/statuses'


@pytest.mark.bdb
@pytest.mark.usefixtures('inputs')
def test_get_transaction_status_endpoint(b, client, user_pk):
    input_tx = b.get_owned_ids(user_pk).pop()
    tx, status = b.get_transaction(input_tx.txid, include_status=True)
    res = client.get(STATUSES_ENDPOINT + '?transaction_id=' + input_tx.txid)
    assert status == res.json['status']
    assert res.json['_links']['tx'] == '/transactions/{}'.format(input_tx.txid)
    assert res.status_code == 200


@pytest.mark.bdb
def test_get_transaction_status_endpoint_returns_404_if_not_found(client):
    res = client.get(STATUSES_ENDPOINT + '?transaction_id=123')
    assert res.status_code == 404


@pytest.mark.bdb
def test_get_block_status_endpoint_undecided(b, client):
    tx = Transaction.create([b.me], [([b.me], 1)])
    tx = tx.sign([b.me_private])

    block = b.create_block([tx])
    b.write_block(block)

    status = b.block_election_status(block)

    res = client.get(STATUSES_ENDPOINT + '?block_id=' + block.id)
    assert status == res.json['status']
    assert '_links' not in res.json
    assert res.status_code == 200


@pytest.mark.bdb
@pytest.mark.usefixtures('inputs')
def test_get_block_status_endpoint_valid(b, client):
    tx = Transaction.create([b.me], [([b.me], 1)])
    tx = tx.sign([b.me_private])

    block = b.create_block([tx])
    b.write_block(block)

    # vote the block valid
    vote = b.vote(block.id, b.get_last_voted_block().id, True)
    b.write_vote(vote)

    status = b.block_election_status(block)

    res = client.get(STATUSES_ENDPOINT + '?block_id=' + block.id)
    assert status == res.json['status']
    assert '_links' not in res.json
    assert res.status_code == 200


@pytest.mark.bdb
@pytest.mark.usefixtures('inputs')
def test_get_block_status_endpoint_invalid(b, client):
    tx = Transaction.create([b.me], [([b.me], 1)])
    tx = tx.sign([b.me_private])

    block = b.create_block([tx])
    b.write_block(block)

    # vote the block valid
    vote = b.vote(block.id, b.get_last_voted_block().id, False)
    b.write_vote(vote)

    status = b.block_election_status(block)

    res = client.get(STATUSES_ENDPOINT + '?block_id=' + block.id)
    assert status == res.json['status']
    assert '_links' not in res.json
    assert res.status_code == 200


@pytest.mark.bdb
def test_get_block_status_endpoint_returns_404_if_not_found(client):
    res = client.get(STATUSES_ENDPOINT + '?block_id=123')
    assert res.status_code == 404


@pytest.mark.bdb
def test_get_status_endpoint_returns_400_bad_query_params(client):
    res = client.get(STATUSES_ENDPOINT)
    assert res.status_code == 400

    res = client.get(STATUSES_ENDPOINT + '?ts_id=123')
    assert res.status_code == 400

    res = client.get(STATUSES_ENDPOINT + '?transaction_id=123&block_id=123')
    assert res.status_code == 400
