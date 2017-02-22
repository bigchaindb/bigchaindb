import pytest
from unittest.mock import MagicMock

pytestmark = pytest.mark.bdb


@pytest.mark.skipif(reason='Will be handled by #1126')
def test_asset_id_index():
    from bigchaindb.backend.mongodb.query import get_txids_filtered
    from bigchaindb.backend import connect

    # Passes a mock in place of a connection to get the query params from the
    # query function, then gets the explain plan from MongoDB to test that
    # it's using certain indexes.

    m = MagicMock()
    get_txids_filtered(m, '')
    pipeline = m.db['bigchain'].aggregate.call_args[0][0]
    run = connect().db.command
    res = run('aggregate', 'bigchain', pipeline=pipeline, explain=True)
    stages = (res['stages'][0]['$cursor']['queryPlanner']['winningPlan']
                 ['inputStage']['inputStages'])
    indexes = [s['inputStage']['indexName'] for s in stages]
    assert set(indexes) == {'asset_id', 'transaction_id'}
