def tests_event_handler():
    from bigchaindb.events import (EventTypes, Event, EventHandler,
                                   setup_events_queue)

    # create and event
    event_data = {'msg': 'some data'}
    event = Event(EventTypes.BLOCK_VALID, event_data)
    # create the events queue
    events_queue = setup_events_queue()

    # create event handler
    event_handler = EventHandler(events_queue)

    # push and event to the queue
    event_handler.put_event(event)

    # get the event from the queue
    event_from_queue = event_handler.get_event()

    assert event_from_queue.type == event.type
    assert event_from_queue.data == event.data
