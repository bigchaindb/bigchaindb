def test_event_handler():
    from bigchaindb.events import EventTypes, Event, PubSub

    # create and event
    event_data = {'msg': 'some data'}
    event = Event(EventTypes.BLOCK_VALID, event_data)

    # create the events pub sub
    pubsub = PubSub()

    sub0 = pubsub.get_subscriber_queue()
    sub1 = pubsub.get_subscriber_queue()

    # push and event to the queue
    pubsub.publish(event)

    # get the event from the queue
    event_sub0 = sub0.get()
    event_sub1 = sub1.get()

    assert event_sub0.type == event.type
    assert event_sub0.data == event.data

    assert event_sub1.type == event.type
    assert event_sub1.data == event.data
