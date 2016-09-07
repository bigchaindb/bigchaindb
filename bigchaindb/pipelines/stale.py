"""This module monitors for stale transactions.

It reassigns transactions which have been assigned a node but
remain in the backlog past a certain amount of time.
"""

import logging
from multipipes import Pipeline, Node
from bigchaindb import Bigchain


logger = logging.getLogger(__name__)


class StaleTransactionMonitor:
    """This class encapsulates the logic for re-assigning stale transactions.

    Note:
        Methods of this class will be executed in different processes.
    """

    def __init__(self, backlog_reassign_delay=5):
        """Initialize StaleTransaction monitor

        Args:
            timeout (int): how often to check for stale tx (in sec)
        """
        self.bigchain = Bigchain(backlog_reassign_delay=backlog_reassign_delay)

    def check_transactions(self):
        """Poll backlog for stale transactions

        Returns:
            txs (list): txs to be re assigned
        """
        return list(self.bigchain.get_stale_transactions())

    def reassign_transactions(self, txs):
        """Put tx back in backlog with new assignee

        Returns:
            database response
        """
        for tx in txs:
            self.bigchain.reassign_transaction(tx)
        return len(txs)


def create_pipeline(timeout=5):
    """Create and return the pipeline of operations to be distributed
    on different processes."""

    stm = StaleTransactionMonitor()

    monitor_pipeline = Pipeline([
        Node(stm.check_transactions, timeout=timeout),
        Node(stm.reassign_transactions)
    ])

    return monitor_pipeline


def start(timeout=5):
    """Create, start, and return the block pipeline."""
    pipeline = create_pipeline()
    pipeline.setup()
    pipeline.start()
    return pipeline
