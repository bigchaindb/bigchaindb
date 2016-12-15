import pytest
from unittest.mock import Mock

from multipipes import Pipe

import bigchaindb
from bigchaindb import Bigchain
from bigchaindb.backend import connect


@pytest.fixture
def mock_changefeed_data():
    return [
        {
            'new_val': 'seems like we have an insert here',
            'old_val': None,
        }, {
            'new_val': None,
            'old_val': 'seems like we have a delete here',
        }, {
            'new_val': 'seems like we have an update here',
            'old_val': 'seems like we have an update here',
        }
    ]


@pytest.fixture
def mock_changefeed_connection(mock_changefeed_data):
    connection = connect(**bigchaindb.config['database'])
    connection.run = Mock(return_value=mock_changefeed_data)
    return connection


def test_changefeed_insert(mock_changefeed_connection):
    from bigchaindb.backend import get_changefeed
    from bigchaindb.backend.changefeed import ChangeFeed

    outpipe = Pipe()
    changefeed = get_changefeed(mock_changefeed_connection,
                                'backlog', ChangeFeed.INSERT)
    changefeed.outqueue = outpipe
    changefeed.run_forever()
    assert outpipe.get() == 'seems like we have an insert here'
    assert outpipe.qsize() == 0


def test_changefeed_delete(mock_changefeed_connection):
    from bigchaindb.backend import get_changefeed
    from bigchaindb.backend.changefeed import ChangeFeed

    outpipe = Pipe()
    changefeed = get_changefeed(mock_changefeed_connection,
                                'backlog', ChangeFeed.DELETE)
    changefeed.outqueue = outpipe
    changefeed.run_forever()
    assert outpipe.get() == 'seems like we have a delete here'
    assert outpipe.qsize() == 0


def test_changefeed_update(mock_changefeed_connection):
    from bigchaindb.backend import get_changefeed
    from bigchaindb.backend.changefeed import ChangeFeed

    outpipe = Pipe()
    changefeed = get_changefeed(mock_changefeed_connection,
                                'backlog', ChangeFeed.UPDATE)
    changefeed.outqueue = outpipe
    changefeed.run_forever()
    assert outpipe.get() == 'seems like we have an update here'
    assert outpipe.qsize() == 0


def test_changefeed_multiple_operations(mock_changefeed_connection):
    from bigchaindb.backend import get_changefeed
    from bigchaindb.backend.changefeed import ChangeFeed

    outpipe = Pipe()
    changefeed = get_changefeed(mock_changefeed_connection, 'backlog',
                                ChangeFeed.INSERT | ChangeFeed.UPDATE)
    changefeed.outqueue = outpipe
    changefeed.run_forever()
    assert outpipe.get() == 'seems like we have an insert here'
    assert outpipe.get() == 'seems like we have an update here'
    assert outpipe.qsize() == 0


def test_changefeed_prefeed(mock_changefeed_connection):
    from bigchaindb.backend import get_changefeed
    from bigchaindb.backend.changefeed import ChangeFeed

    outpipe = Pipe()
    changefeed = get_changefeed(mock_changefeed_connection, 'backlog',
                                ChangeFeed.INSERT, prefeed=[1, 2, 3])
    changefeed.outqueue = outpipe
    changefeed.run_forever()
    assert outpipe.qsize() == 4
