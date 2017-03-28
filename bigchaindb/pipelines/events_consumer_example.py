import multiprocessing as mp

from bigchaindb.events import EventHandler


def consume_events(events_queue):
    event_handler = EventHandler(events_queue)
    while True:
        event = event_handler.get_event()
        print('Event type: {} Event data: {}'.format(event.type, event.data))


def events_consumer(events_queue):
    return mp.Process(target=consume_events, args=(events_queue,))
