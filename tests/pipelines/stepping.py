"""
Pipeline stepping is a way to advance the asynchronous data pipeline
deterministically by exposing each step separately and advancing the states
manually.

The multipipes.Pipeline class implements a pipeline that advanced
asynchronously and concurrently. This module provides an interface to the
BigchainDB pipelines that is static, ie, does not advance without prompting.

Rather than having a pipeline that is in an all or nothing running / not running
state, one can do the following:


steps = create_stepper()

with steps.start():
    tx = my_create_and_write_tx()
    steps.block_changefeed(timeout=1)
    steps.block_filter_tx()
    steps.block_validate_tx()
    steps.block_create(timeout=True)

assert steps.counts == {'block_write': 1}

Pending items are held in the `.queues` attribute, and every task has it's own
queue (as in multipipes.Pipeline). Queues are just lists though so they can
be easily inspected.

As a shortcut, the `.counts` attribute is provided which returns the number of
pending items for each task. This is useful to assert the expected status of
the queues after performing some sequence.
"""


import functools
import time
import types
import logging
from contextlib import contextmanager
from unittest.mock import patch

import bigchaindb.core
from bigchaindb.backend.changefeed import ChangeFeed
import bigchaindb.pipelines.block
import bigchaindb.pipelines.stale


class MultipipesStepper:
    def __init__(self):
        self.queues = {}
        self.tasks = {}
        self.input_tasks = set()
        self.processes = []

    def add_input(self, prefix, node, next):
        name = '%s_%s' % (prefix, node.name)
        next_name = '%s_%s' % (prefix, next.name)

        if isinstance(node, ChangeFeed):
            self.processes.append(node)

            def f(*args, **kwargs):
                _kwargs = {'timeout': 0.1}
                _kwargs.update(kwargs)
                return node.outqueue.get(*args, **kwargs)
        else:
            f = node.target

        def inner(**kwargs):
            r = f(**kwargs)
            if r is not None:
                self.enqueue(next_name, r)

        self.tasks[name] = functools.wraps(f)(inner)
        self.input_tasks.add(name)

    def add_stage(self, prefix, node, next):
        """
        Convert pipeline stage into task.
        """
        f = node.target
        name = '%s_%s' % (prefix, node.name)
        if next:
            next_name = '%s_%s' % (prefix, next.name)

        def inner(*args):
            out = f(*args)
            if out is not None and next:
                self.enqueue(next_name, out)

        task = functools.wraps(f)(inner)
        self.tasks[name] = task

    def enqueue(self, name, item):
        queue = self.queues.setdefault(name, [])
        if isinstance(item, types.GeneratorType):
            queue.extend(list(item))
        else:
            queue.append(item)

    def step(self, name, **kwargs):
        logging.debug('Stepping %s', name)
        task = self.tasks[name]
        if name in self.input_tasks:
            task(**kwargs)
        else:
            queue = self.queues.get(name, [])
            if not queue:
                raise Empty(name)
            task(queue.pop(0), **kwargs)
        logging.debug('Stepped %s', name)

    def get_counts(self):
        counts = {}
        for name in self.queues:
            n = len(self.queues[name])
            if n:
                counts[name] = n
        return counts

    def __getattr__(self, name):
        return lambda **kwargs: self.step(name, **kwargs)

    @contextmanager
    def start(self):
        for p in self.processes:
            p.start()
        # It would be nice to have a better way to wait for changefeeds here.
        # We have to wait some amount of time because the feed setup is
        # happening in a different process and won't include any writes we
        # perform before it is ready.
        time.sleep(0.2)
        try:
            yield
        finally:
            for p in self.processes:
                p.terminate()


class Empty(Exception):
    pass


def update_stepper(stepper, prefix, pipeline):
    nodes = pipeline.nodes
    for i in range(len(nodes)):
        n0 = nodes[i]
        n1 = (nodes + [None])[i+1]
        f = stepper.add_input if i == 0 else stepper.add_stage
        f(prefix, n0, n1)


def create_stepper():
    stepper = MultipipesStepper()

    with patch('bigchaindb.pipelines.block.Pipeline.start'):
        pipeline = bigchaindb.pipelines.block.start()
        update_stepper(stepper, 'block', pipeline)

    with patch('bigchaindb.pipelines.stale.Pipeline.start'):
        pipeline = bigchaindb.pipelines.stale.start(
            timeout=0, backlog_reassign_delay=0)
        update_stepper(stepper, 'stale', pipeline)

    return stepper
