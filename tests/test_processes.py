from unittest.mock import patch

from multiprocessing import Process
from bigchaindb.pipelines import vote, block, election, stale


@patch.object(stale, 'start')
@patch.object(election, 'start')
@patch.object(block, 'start')
@patch.object(vote, 'start')
@patch.object(Process, 'start')
@patch('bigchaindb.events.Exchange.get_publisher_queue', spec_set=True, autospec=True)
@patch('bigchaindb.events.Exchange.run', spec_set=True, autospec=True)
def test_processes_start(mock_exchange_run, mock_exchange, mock_process, mock_vote,
                         mock_block, mock_election, mock_stale):
    from bigchaindb import processes

    processes.start()

    mock_vote.assert_called_with()
    mock_block.assert_called_with()
    mock_stale.assert_called_with()
    mock_process.assert_called_with()
    mock_election.assert_called_once_with(
        events_queue=mock_exchange.return_value)


@patch.object(Process, 'start')
def test_start_events_plugins(mock_process, monkeypatch):

    class MockPlugin:
        def __init__(self, event_types):
            self.event_types = event_types

        def run(self, queue):
            pass

    monkeypatch.setattr('bigchaindb.config_utils.load_events_plugins',
                        lambda names: [('one', MockPlugin(1)),
                                       ('two', MockPlugin(2))])

    from bigchaindb import processes
    from bigchaindb.events import Exchange

    exchange = Exchange()
    processes.start_events_plugins(exchange)
    assert len(exchange.queues) == 2
