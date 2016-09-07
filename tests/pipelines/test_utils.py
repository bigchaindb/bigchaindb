from unittest.mock import patch

import rethinkdb

from multipipes import Pipe
from bigchaindb.pipelines.utils import ChangeFeed


MOCK_CHANGEFEED_DATA = [{
    'new_val': 'seems like we have an insert here',
    'old_val': None,
}, {
    'new_val': None,
    'old_val': 'seems like we have a delete here',
}, {
    'new_val': 'seems like we have an update here',
    'old_val': 'seems like we have an update here',
}]


@patch.object(rethinkdb.ast.RqlQuery, 'run', return_value=MOCK_CHANGEFEED_DATA)
def test_changefeed_insert(mock_run):
    outpipe = Pipe()
    changefeed = ChangeFeed('backlog', ChangeFeed.INSERT)
    changefeed.outqueue = outpipe
    changefeed.run_forever()
    assert outpipe.get() == 'seems like we have an insert here'
    assert outpipe.qsize() == 0


@patch.object(rethinkdb.ast.RqlQuery, 'run', return_value=MOCK_CHANGEFEED_DATA)
def test_changefeed_delete(mock_run):
    outpipe = Pipe()
    changefeed = ChangeFeed('backlog', ChangeFeed.DELETE)
    changefeed.outqueue = outpipe
    changefeed.run_forever()
    assert outpipe.get() == 'seems like we have a delete here'
    assert outpipe.qsize() == 0


@patch.object(rethinkdb.ast.RqlQuery, 'run', return_value=MOCK_CHANGEFEED_DATA)
def test_changefeed_update(mock_run):
    outpipe = Pipe()
    changefeed = ChangeFeed('backlog', ChangeFeed.UPDATE)
    changefeed.outqueue = outpipe
    changefeed.run_forever()
    assert outpipe.get() == 'seems like we have an update here'
    assert outpipe.qsize() == 0


@patch.object(rethinkdb.ast.RqlQuery, 'run', return_value=MOCK_CHANGEFEED_DATA)
def test_changefeed_multiple_operations(mock_run):
    outpipe = Pipe()
    changefeed = ChangeFeed('backlog', ChangeFeed.INSERT | ChangeFeed.UPDATE)
    changefeed.outqueue = outpipe
    changefeed.run_forever()
    assert outpipe.get() == 'seems like we have an insert here'
    assert outpipe.get() == 'seems like we have an update here'
    assert outpipe.qsize() == 0


@patch.object(rethinkdb.ast.RqlQuery, 'run', return_value=MOCK_CHANGEFEED_DATA)
def test_changefeed_prefeed(mock_run):
    outpipe = Pipe()
    changefeed = ChangeFeed('backlog', ChangeFeed.INSERT, prefeed=[1, 2, 3])
    changefeed.outqueue = outpipe
    changefeed.run_forever()
    assert outpipe.qsize() == 4
