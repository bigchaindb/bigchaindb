def test_event_handler():
    from bigchaindb.events import EventTypes, Event, Exchange

    # create and event
    event_data = {'msg': 'some data'}
    event = Event(EventTypes.BLOCK_VALID, event_data)

    # create the events pub sub
    exchange = Exchange()

    sub0 = exchange.get_subscriber_queue(EventTypes.BLOCK_VALID)
    sub1 = exchange.get_subscriber_queue(EventTypes.BLOCK_VALID |
                                         EventTypes.BLOCK_INVALID)
    # Subscribe to all events
    sub2 = exchange.get_subscriber_queue()
    sub3 = exchange.get_subscriber_queue(EventTypes.BLOCK_INVALID)

    # push and event to the queue
    exchange.dispatch(event)

    # get the event from the queue
    event_sub0 = sub0.get()
    event_sub1 = sub1.get()
    event_sub2 = sub2.get()

    assert event_sub0.type == event.type
    assert event_sub0.data == event.data

    assert event_sub1.type == event.type
    assert event_sub1.data == event.data

    assert event_sub2.type == event.type
    assert event_sub2.data == event.data

    assert sub3.qsize() == 0


def test_exchange_stops_with_poison_pill():
    from bigchaindb.events import EventTypes, Event, Exchange, POISON_PILL

    # create and event
    event_data = {'msg': 'some data'}
    event = Event(EventTypes.BLOCK_VALID, event_data)

    # create the events pub sub
    exchange = Exchange()

    publisher_queue = exchange.get_publisher_queue()

    # push and event to the queue
    publisher_queue.put(event)
    publisher_queue.put(POISON_PILL)
    exchange.run()

    assert publisher_queue.qsize() == 0
