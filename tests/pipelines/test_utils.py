from unittest.mock import patch

import rethinkdb

from multipipes import Pipe
from bigchaindb.pipelines import utils


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
    changefeed = utils.ChangeFeed('backlog', 'insert')
    changefeed.outqueue = outpipe
    changefeed.run_forever()
    assert outpipe.get() == 'seems like we have an insert here'


@patch.object(rethinkdb.ast.RqlQuery, 'run', return_value=MOCK_CHANGEFEED_DATA)
def test_changefeed_delete(mock_run):
    outpipe = Pipe()
    changefeed = utils.ChangeFeed('backlog', 'delete')
    changefeed.outqueue = outpipe
    changefeed.run_forever()
    assert outpipe.get() == 'seems like we have a delete here'


@patch.object(rethinkdb.ast.RqlQuery, 'run', return_value=MOCK_CHANGEFEED_DATA)
def test_changefeed_update(mock_run):
    outpipe = Pipe()
    changefeed = utils.ChangeFeed('backlog', 'update')
    changefeed.outqueue = outpipe
    changefeed.run_forever()
    assert outpipe.get() == {'new_val': 'seems like we have an update here',
                             'old_val': 'seems like we have an update here'}


@patch.object(rethinkdb.ast.RqlQuery, 'run', return_value=MOCK_CHANGEFEED_DATA)
def test_changefeed_prefeed(mock_run):
    outpipe = Pipe()
    changefeed = utils.ChangeFeed('backlog', 'insert', prefeed=[1, 2, 3])
    changefeed.outqueue = outpipe
    changefeed.run_forever()
    assert outpipe.qsize() == 4

