from unittest.mock import patch

from multiprocessing import Process
from bigchaindb.pipelines import vote, block, election, stale


@patch.object(stale, 'start')
@patch.object(election, 'start')
@patch.object(block, 'start')
@patch.object(vote, 'start')
@patch.object(Process, 'start')
@patch('bigchaindb.events.setup_events_queue', spec_set=True, autospec=True)
def test_processes_start(mock_setup_events_queue, mock_process, mock_vote,
                         mock_block, mock_election, mock_stale):
    from bigchaindb import processes

    processes.start()

    mock_vote.assert_called_with()
    mock_block.assert_called_with()
    mock_stale.assert_called_with()
    mock_process.assert_called_with()
    mock_election.assert_called_once_with(
        events_queue=mock_setup_events_queue.return_value)
