import pytest
from flask import url_for

from bigchaindb.models import Transaction


@pytest.mark.bdb
@pytest.mark.usefixtures('inputs')
def test_get_transaction_status_endpoint(b, client, user_pk):
    from bigchaindb.web.views.statuses import StatusApi
    from bigchaindb.web.views.transactions import TransactionApi
    input_tx = b.get_owned_ids(user_pk).pop()
    tx, status = b.get_transaction(input_tx.txid, include_status=True)
    path = url_for(StatusApi.__name__.lower(), tx_id=input_tx.txid)
    res = client.get(path=path)
    assert status == res.json['status']
    expected_tx_link = url_for(
        TransactionApi.__name__.lower(), tx_id=input_tx.txid)[7:]
    assert res.json['_links']['tx'] == expected_tx_link
    assert res.status_code == 200


@pytest.mark.bdb
def test_get_transaction_status_endpoint_returns_404_if_not_found(client):
    from bigchaindb.web.views.statuses import StatusApi
    path = url_for(StatusApi.__name__.lower(), tx_id=123)
    res = client.get(path=path)
    assert res.status_code == 404


@pytest.mark.bdb
def test_get_block_status_endpoint_undecided(b, client):
    from bigchaindb.web.views.statuses import StatusApi
    tx = Transaction.create([b.me], [([b.me], 1)])
    tx = tx.sign([b.me_private])

    block = b.create_block([tx])
    b.write_block(block)

    status = b.block_election_status(block.id, block.voters)

    path = url_for(StatusApi.__name__.lower(), block_id=block.id)
    res = client.get(path=path)
    assert status == res.json['status']
    assert '_links' not in res.json
    assert res.status_code == 200


@pytest.mark.bdb
@pytest.mark.usefixtures('inputs')
def test_get_block_status_endpoint_valid(b, client):
    from bigchaindb.web.views.statuses import StatusApi
    tx = Transaction.create([b.me], [([b.me], 1)])
    tx = tx.sign([b.me_private])

    block = b.create_block([tx])
    b.write_block(block)

    # vote the block valid
    vote = b.vote(block.id, b.get_last_voted_block().id, True)
    b.write_vote(vote)

    status = b.block_election_status(block.id, block.voters)

    path = url_for(StatusApi.__name__.lower(), block_id=block.id)
    res = client.get(path=path)
    assert status == res.json['status']
    assert '_links' not in res.json
    assert res.status_code == 200


@pytest.mark.bdb
@pytest.mark.usefixtures('inputs')
def test_get_block_status_endpoint_invalid(b, client):
    from bigchaindb.web.views.statuses import StatusApi
    tx = Transaction.create([b.me], [([b.me], 1)])
    tx = tx.sign([b.me_private])

    block = b.create_block([tx])
    b.write_block(block)

    # vote the block valid
    vote = b.vote(block.id, b.get_last_voted_block().id, False)
    b.write_vote(vote)

    status = b.block_election_status(block.id, block.voters)

    path = url_for(StatusApi.__name__.lower(), block_id=block.id)
    res = client.get(path=path)
    assert status == res.json['status']
    assert '_links' not in res.json
    assert res.status_code == 200


@pytest.mark.bdb
def test_get_block_status_endpoint_returns_404_if_not_found(client):
    from bigchaindb.web.views.statuses import StatusApi
    path = url_for(StatusApi.__name__.lower(), block_id=123)
    res = client.get(path=path)
    assert res.status_code == 404


@pytest.mark.bdb
@pytest.mark.parametrize('query_params', (
    {}, {'ts_id': 123}, {'tx_id': 123, 'block_id': 123}
))
def test_get_status_endpoint_returns_400_bad_query_params(client,
                                                          query_params):
    from bigchaindb.web.views.statuses import StatusApi
    path = url_for(StatusApi.__name__.lower(), **query_params)
    res = client.get(path)
    assert res.status_code == 400
