import pytest
from unittest.mock import Mock

from multipipes import Pipe
from bigchaindb import Bigchain
from bigchaindb.backend.connection import Connection
from bigchaindb.pipelines.utils import ChangeFeed


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
def mock_changefeed_bigchain(mock_changefeed_data):
    connection = Connection(host=None, port=None, dbname=None)
    connection.run = Mock(return_value=mock_changefeed_data)
    return Bigchain(connection=connection)


def test_changefeed_insert(mock_changefeed_bigchain):
    outpipe = Pipe()
    changefeed = ChangeFeed('backlog', ChangeFeed.INSERT, bigchain=mock_changefeed_bigchain)
    changefeed.outqueue = outpipe
    changefeed.run_forever()
    assert outpipe.get() == 'seems like we have an insert here'
    assert outpipe.qsize() == 0


def test_changefeed_delete(mock_changefeed_bigchain):
    outpipe = Pipe()
    changefeed = ChangeFeed('backlog', ChangeFeed.DELETE, bigchain=mock_changefeed_bigchain)
    changefeed.outqueue = outpipe
    changefeed.run_forever()
    assert outpipe.get() == 'seems like we have a delete here'
    assert outpipe.qsize() == 0


def test_changefeed_update(mock_changefeed_bigchain):
    outpipe = Pipe()
    changefeed = ChangeFeed('backlog', ChangeFeed.UPDATE, bigchain=mock_changefeed_bigchain)
    changefeed.outqueue = outpipe
    changefeed.run_forever()
    assert outpipe.get() == 'seems like we have an update here'
    assert outpipe.qsize() == 0


def test_changefeed_multiple_operations(mock_changefeed_bigchain):
    outpipe = Pipe()
    changefeed = ChangeFeed('backlog',
                            ChangeFeed.INSERT | ChangeFeed.UPDATE,
                            bigchain=mock_changefeed_bigchain)
    changefeed.outqueue = outpipe
    changefeed.run_forever()
    assert outpipe.get() == 'seems like we have an insert here'
    assert outpipe.get() == 'seems like we have an update here'
    assert outpipe.qsize() == 0


def test_changefeed_prefeed(mock_changefeed_bigchain):
    outpipe = Pipe()
    changefeed = ChangeFeed('backlog',
                            ChangeFeed.INSERT,
                            prefeed=[1, 2, 3],
                            bigchain=mock_changefeed_bigchain)
    changefeed.outqueue = outpipe
    changefeed.run_forever()
    assert outpipe.qsize() == 4
