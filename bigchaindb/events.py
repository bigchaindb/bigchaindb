from queue import Empty
from collections import defaultdict
from multiprocessing import Queue


POISON_PILL = 'POISON_PILL'


class EventTypes:
    """Container class that holds all the possible
    events BigchainDB manages.
    """

    # If you add a new Event Type, make sure to add it
    # to the docs in docs/server/source/event-plugin-api.rst
    ALL = ~0
    BLOCK_VALID = 1
    BLOCK_INVALID = 2
    # NEW_EVENT = 4
    # NEW_EVENT = 8
    # NEW_EVENT = 16...


class Event:
    """An Event."""

    def __init__(self, event_type, event_data):
        """Creates a new event.

        Args:
            event_type (int): the type of the event, see
                :class:`~bigchaindb.events.EventTypes`
            event_data (obj): the data of the event.
        """

        self.type = event_type
        self.data = event_data


class Exchange:
    """Dispatch events to subscribers."""

    def __init__(self):
        self.publisher_queue = Queue()
        self.started_queue = Queue()

        # Map <event_types -> queues>
        self.queues = defaultdict(list)

    def get_publisher_queue(self):
        """Get the queue used by the publisher.

        Returns:
            a :class:`multiprocessing.Queue`.
        """

        return self.publisher_queue

    def get_subscriber_queue(self, event_types=None):
        """Create a new queue for a specific combination of event types
        and return it.

        Returns:
            a :class:`multiprocessing.Queue`.
        Raises:
            RuntimeError if called after `run`
        """

        try:
            self.started_queue.get_nowait()
            raise RuntimeError('Cannot create a new subscriber queue while Exchange is running.')
        except Empty:
            pass

        if event_types is None:
            event_types = EventTypes.ALL

        queue = Queue()
        self.queues[event_types].append(queue)
        return queue

    def dispatch(self, event):
        """Given an event, send it to all the subscribers.

        Args
            event (:class:`~bigchaindb.events.EventTypes`): the event to
                dispatch to all the subscribers.
        """

        for event_types, queues in self.queues.items():
            if event.type & event_types:
                for queue in queues:
                    queue.put(event)

    def run(self):
        """Start the exchange"""
        self.started_queue.put('STARTED')

        while True:
            event = self.publisher_queue.get()
            if event == POISON_PILL:
                return
            else:
                self.dispatch(event)
