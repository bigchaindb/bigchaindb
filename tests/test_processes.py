from unittest.mock import patch

from multiprocessing import Process
from bigchaindb.pipelines import vote, block, election, stale


@patch.object(stale, 'start')
@patch.object(election, 'start')
@patch.object(block, 'start')
@patch.object(vote, 'start')
@patch.object(Process, 'start')
def test_processes_start(mock_vote, mock_block, mock_election, mock_stale,
                         mock_process):
    from bigchaindb import processes

    processes.start()

    mock_vote.assert_called_with()
    mock_block.assert_called_with()
    mock_election.assert_called_with()
    mock_stale.assert_called_with()
    mock_process.assert_called_with()

