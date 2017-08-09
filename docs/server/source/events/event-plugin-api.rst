The Event Plugin API [experimental]
===================================

.. danger::
    The Event Plugin API is **experimental** and might change in the future.

BigchainDB implements an internal event system that allows different software
components to receive updates on specific topics. The WebSocket API, for example,
is a subscriber to a stream of events called ``BLOCK_VALID``. Every time a block is
voted valid, the WebSocket API is notified, and it sends updates to all the
clients connected.

We decided to make this internal event system public, to allow developers to
integrate BigchainDB with other applications, such as AMPQ systems.


Available events
----------------

The event types are listed in the source file ``bigchaindb/events.py``.

.. list-table:: Event Types
   :widths: 15 10 30
   :header-rows: 1

   * - event name
     - event id
     - description
   * - BLOCK_VALID
     - 1
     - a block has been voted valid by the network.
   * - BLOCK_INVALID
     - 2
     - a block has been voted invalid by the network.



Plugin Example
----------------

We developed a minimal plugin that listens to new valid blocks and prints them
to the console:

- https://github.com/bigchaindb/bigchaindb_events_plugin_example


Architecture of an Event Plugin
-------------------------------

Creating your own plugin is really easy, and can be summarized in few steps:

1. Create a new Python package that defines the entry point ``bigchaindb.events`` in its ``setup.py``.
2. In your entry point, define two properties:

   - ``events_types``: a variable to tell BigchainDB to which events your plugin is interested.
   - ``run``: a function that will process the events coming from BigchainDB.
3. Install the newly created Python in the current environment.
4. Add the plugin name to your BigchainDB configuration.
5. (Re)start BigchainDB

If the installation was successful, the plugin will be run in a different
process. Your plugin will receive events through a ``multiprocessing.Queue``
object. Remember: it's your plugin responsibility to consume that queue.

A plugin can subscribe to more than one events by combining them using the
**binary or** operator, e.g. in case you want to subscribe to both valid and
invalid blocks your ``events_types`` can be ``1 | 2``.
