import pytest
from bigchaindb.pipelines import block, election, vote, stale


@pytest.fixture
def processes(b):
    b.create_genesis_block()
    block_maker = block.start()
    voter = vote.start()
    election_runner = election.start()
    stale_monitor = stale.start()
    yield
    block_maker.terminate()
    voter.terminate()
    election_runner.terminate()
    stale_monitor.terminate()
