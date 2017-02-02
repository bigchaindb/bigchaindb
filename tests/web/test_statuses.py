from functools import singledispatch

import pytest
from flask import url_for

from bigchaindb.models import Transaction

APPLICATION_ROOT = '/api/v1'


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
        TransactionApi.__name__.lower(), tx_id=input_tx.txid
    ).replace(APPLICATION_ROOT, '')
    assert res.json['_links']['tx'] == expected_tx_link
    assert res.status_code == 200


@pytest.mark.bdb
def test_get_backlog_transaction_status(b, client, backlog_tx):
    from bigchaindb import Bigchain
    from bigchaindb.web.views.statuses import StatusApi
    from bigchaindb.web.views.transactions import TransactionApi
    path = url_for(StatusApi.__name__.lower(), tx_id=backlog_tx.id)
    res = client.get(path=path)
    assert res.json['status'] == Bigchain.TX_IN_BACKLOG
    expected_tx_link = url_for(
        TransactionApi.__name__.lower(), tx_id=backlog_tx.id
    ).replace(APPLICATION_ROOT, '')
    assert res.json['_links']['tx'] == expected_tx_link
    assert res.status_code == 200


@pytest.mark.bdb
def test_get_undecided_transaction_status(b, client, undecided_tx):
    from bigchaindb import Bigchain
    from bigchaindb.web.views.statuses import StatusApi
    from bigchaindb.web.views.transactions import TransactionApi
    path = url_for(StatusApi.__name__.lower(), tx_id=undecided_tx.id)
    res = client.get(path=path)
    assert res.json['status'] == Bigchain.BLOCK_UNDECIDED
    expected_tx_link = url_for(
        TransactionApi.__name__.lower(), tx_id=undecided_tx.id
    ).replace(APPLICATION_ROOT, '')
    assert res.json['_links']['tx'] == expected_tx_link
    assert res.status_code == 200


@pytest.mark.bdb
def test_get_valid_transaction_status(b, client, valid_tx):
    from bigchaindb import Bigchain
    from bigchaindb.web.views.statuses import StatusApi
    from bigchaindb.web.views.transactions import TransactionApi
    path = url_for(StatusApi.__name__.lower(), tx_id=valid_tx.id)
    res = client.get(path=path)
    assert res.json['status'] == Bigchain.BLOCK_VALID
    expected_tx_link = url_for(
        TransactionApi.__name__.lower(), tx_id=valid_tx.id
    ).replace(APPLICATION_ROOT, '')
    assert res.json['_links']['tx'] == expected_tx_link
    assert res.status_code == 200


@pytest.mark.bdb
def test_get_invalid_transaction_status(b, client, invalid_tx):
    from bigchaindb import Bigchain
    from bigchaindb.web.views.statuses import StatusApi
    from bigchaindb.web.views.transactions import TransactionApi
    path = url_for(StatusApi.__name__.lower(), tx_id=invalid_tx.id)
    res = client.get(path=path)
    assert res.json['status'] == Bigchain.BLOCK_INVALID
    expected_tx_link = url_for(
        TransactionApi.__name__.lower(), tx_id=invalid_tx.id
    ).replace(APPLICATION_ROOT, '')
    assert res.json['_links']['tx'] == expected_tx_link
    assert res.status_code == 200


@pytest.mark.parametrize('statuses,in_backlog,status', (
    (None, True, 'backlog'),
    ({'block-001': 'valid'}, True, 'valid'),
    ({'block-001': 'undecided'}, True, 'undecided'),
    ({'block-001': 'invalid'}, True, 'backlog'),
    ({'block-001': 'invalid'}, False, 'invalid'),
    ({'block-001': 'valid', 'block-002': 'undecided'}, True, 'valid'),
    ({'block-001': 'valid', 'block-002': 'invalid'}, True, 'valid'),
    ({'block-002': 'undecided', 'block-003': 'invalid'}, True, 'undecided'),
    ({'block-001': 'valid', 'block-002': 'undecided', 'block-003': 'invalid'},
     True,
     'valid'),
))
def test_get_transaction_status_mocked(client, statuses,
                                       status, in_backlog, monkeypatch):
    from bigchaindb.web.views.statuses import StatusApi
    from bigchaindb.web.views.transactions import TransactionApi
    from bigchaindb.backend.rethinkdb.connection import RethinkDBConnection
    from bigchaindb.backend.mongodb.connection import MongoDBConnection

    @singledispatch
    def mocked_get_transaction_from_backlog(conn, txid):
        return in_backlog

    mocked_get_transaction_from_backlog.register(RethinkDBConnection,
                                                 lambda x, y: in_backlog)
    mocked_get_transaction_from_backlog.register(MongoDBConnection,
                                                 lambda x, y: in_backlog)
    monkeypatch.setattr(
        'bigchaindb.backend.query.get_transaction_from_backlog',
        mocked_get_transaction_from_backlog,
    )
    monkeypatch.setattr(
        'bigchaindb.core.Bigchain.get_blocks_status_containing_tx',
        lambda self, txid: statuses,
    )
    tx_id = 1
    res = client.get(path=url_for(StatusApi.__name__.lower(), tx_id=tx_id))
    assert res.json['status'] == status
    assert res.json['_links']['tx'] == url_for(
        TransactionApi.__name__.lower(), tx_id=tx_id
    ).replace(APPLICATION_ROOT, '')
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
