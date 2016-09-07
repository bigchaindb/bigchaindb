"""This module monitors for stale transactions.

It reassigns transactions which have been assigned a node but
remain in the backlog past a certain amount of time.
"""

import logging
from multipipes import Pipeline, Node
from bigchaindb import Bigchain
from time import sleep


logger = logging.getLogger(__name__)


class StaleTransactionMonitor:
    """This class encapsulates the logic for re-assigning stale transactions.

    Note:
        Methods of this class will be executed in different processes.
    """

    def __init__(self, timeout=5, backlog_reassign_delay=None):
        """Initialize StaleTransaction monitor

        Args:
            timeout: how often to check for stale tx (in sec)
            backlog_reassign_delay: How stale a transaction should
            be before reassignment (in sec). If supplied, overrides the
            Bigchain default value.
        """
        self.bigchain = Bigchain(backlog_reassign_delay=backlog_reassign_delay)
        self.timeout = timeout

    def check_transactions(self):
        """Poll backlog for stale transactions

        Returns:
            txs (list): txs to be re assigned
        """
        sleep(self.timeout)
        for tx in self.bigchain.get_stale_transactions():
            yield tx

    def reassign_transactions(self, tx):
        """Put tx back in backlog with new assignee

        Returns:
            transaction
        """
        self.bigchain.reassign_transaction(tx)
        return tx


def create_pipeline(timeout=5, backlog_reassign_delay=5):
    """Create and return the pipeline of operations to be distributed
    on different processes."""

    stm = StaleTransactionMonitor(timeout=timeout,
                                  backlog_reassign_delay=backlog_reassign_delay)

    monitor_pipeline = Pipeline([
        Node(stm.check_transactions),
        Node(stm.reassign_transactions)
    ])

    return monitor_pipeline


def start(timeout=5, backlog_reassign_delay=5):
    """Create, start, and return the block pipeline."""
    pipeline = create_pipeline(timeout=timeout,
                               backlog_reassign_delay=backlog_reassign_delay)
    pipeline.setup()
    pipeline.start()
    return pipeline
