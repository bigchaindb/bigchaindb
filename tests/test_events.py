def test_event_handler():
    from bigchaindb.events import EventTypes, Event, PubSub

    # create and event
    event_data = {'msg': 'some data'}
    event = Event(EventTypes.BLOCK_VALID, event_data)

    # create the events pub sub
    pubsub = PubSub()

    sub0 = pubsub.get_subscriber_queue(EventTypes.BLOCK_VALID)
    sub1 = pubsub.get_subscriber_queue(EventTypes.BLOCK_VALID |
                                       EventTypes.BLOCK_INVALID)
    # Subscribe to all events
    sub2 = pubsub.get_subscriber_queue()
    sub3 = pubsub.get_subscriber_queue(EventTypes.BLOCK_INVALID)

    # push and event to the queue
    pubsub.publish(event)

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
