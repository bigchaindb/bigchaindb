from collections import defaultdict
from multiprocessing import Queue


POISON_PILL = 'POISON_PILL'


class EventTypes:

    ALL = ~0
    BLOCK_VALID = 1
    BLOCK_INVALID = 2
    # NEW_EVENT = 4
    # NEW_EVENT = 8
    # NEW_EVENT = 16...


class Event:

    def __init__(self, event_type, event_data):
        self.type = event_type
        self.data = event_data


class PubSub:

    def __init__(self):
        self.publisher_queue = Queue()
        # Map <event_types -> queues>
        self.queues = defaultdict(list)

    def get_publisher_queue(self):
        return self.publisher_queue

    def get_subscriber_queue(self, event_types=EventTypes.ALL):
        queue = Queue()
        self.queues[event_types].append(queue)
        return queue

    def publish(self, event):
        for event_types, queues in self.queues.items():
            if event.type & event_types:
                for queue in queues:
                    queue.put(event)

    def run(self):
        while True:
            event = self.publisher_queue.get()
            if event is POISON_PILL:
                return
            else:
                self.publish(event)
