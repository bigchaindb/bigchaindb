from enum import Enum
from multiprocessing import Queue


POISON_PILL = 'POISON_PILL'


class EventTypes(Enum):
    BLOCK_VALID = 1
    BLOCK_INVALID = 2


class Event:

    def __init__(self, event_type, event_data):
        self.type = event_type
        self.data = event_data


class PubSub:

    def __init__(self):
        self.publisher_queue = Queue()
        self.queues = []

    def get_publisher_queue(self):
        return self.publisher_queue

    def get_subscriber_queue(self):
        queue = Queue()
        self.queues.append(queue)
        return queue

    def publish(self, event):
        for queue in self.queues:
            queue.put(event)

    def run(self):
        while True:
            event = self.publisher_queue.get()
            if event is POISON_PILL:
                return
            else:
                self.publish(event)
