from enum import Enum
from multiprocessing import Queue


class EventTypes(Enum):
    BLOCK_VALID = 1
    BLOCK_INVALID = 2


class Event:

    def __init__(self, event_type, event_data):
        self.type = event_type
        self.data = event_data


class EventHandler:

    def __init__(self, events_queue):
        self.events_queue = events_queue

    def put_event(self, event, timeout=None):
        # TODO: handle timeouts
        self.events_queue.put(event, timeout=None)

    def get_event(self, timeout=None):
        # TODO: handle timeouts
        return self.events_queue.get(timeout=None)


def setup_events_queue():
    # TODO: set bounds to the queue
    return Queue()
