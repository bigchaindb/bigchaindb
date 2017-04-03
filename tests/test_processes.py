from unittest.mock import patch

from multiprocessing import Process, Queue
from bigchaindb.pipelines import vote, block, election, stale


@patch.object(stale, 'start')
@patch.object(election, 'start')
@patch.object(block, 'start')
@patch.object(vote, 'start')
@patch.object(Process, 'start')
def test_processes_start(mock_process, mock_vote, mock_block, mock_election,
                         mock_stale):
    from bigchaindb import processes

    processes.start()

    mock_vote.assert_called_with()
    mock_block.assert_called_with()
    mock_stale.assert_called_with()
    mock_process.assert_called_with()
    assert mock_election.call_count == 1
    # the events queue is declared inside processes.start()
    assert type(mock_election.call_args[1]['events_queue']) == type(Queue())
