# Copyright © 2020 Interplanetary Database Association e.V.,
# BigchainDB and IPDB software contributors.
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

import contextlib
import threading
import queue
import multiprocessing as mp
import json

import setproctitle
from packaging import version
from bigchaindb.version import __tm_supported_versions__
from bigchaindb.tendermint_utils import key_from_base64
from bigchaindb.common.crypto import key_pair_from_ed25519_key


class ProcessGroup(object):

    def __init__(self, concurrency=None, group=None, target=None, name=None,
                 args=None, kwargs=None, daemon=None):
        self.concurrency = concurrency or mp.cpu_count()
        self.group = group
        self.target = target
        self.name = name
        self.args = args or ()
        self.kwargs = kwargs or {}
        self.daemon = daemon
        self.processes = []

    def start(self):
        for i in range(self.concurrency):
            proc = mp.Process(group=self.group, target=self.target,
                              name=self.name, args=self.args,
                              kwargs=self.kwargs, daemon=self.daemon)
            proc.start()
            self.processes.append(proc)


class Process(mp.Process):
    """Wrapper around multiprocessing.Process that uses
    setproctitle to set the name of the process when running
    the target task.
    """

    def run(self):
        setproctitle.setproctitle(self.name)
        super().run()


# Inspired by:
# - http://stackoverflow.com/a/24741694/597097
def pool(builder, size, timeout=None):
    """Create a pool that imposes a limit on the number of stored
    instances.

    Args:
        builder: a function to build an instance.
        size: the size of the pool.
        timeout(Optional[float]): the seconds to wait before raising
            a ``queue.Empty`` exception if no instances are available
            within that time.
    Raises:
        If ``timeout`` is defined but the request is taking longer
        than the specified time, the context manager will raise
        a ``queue.Empty`` exception.

    Returns:
        A context manager that can be used with the ``with``
        statement.

    """

    lock = threading.Lock()
    local_pool = queue.Queue()
    current_size = 0

    @contextlib.contextmanager
    def pooled():
        nonlocal current_size
        instance = None

        # If we still have free slots, then we have room to create new
        # instances.
        if current_size < size:
            with lock:
                # We need to check again if we have slots available, since
                # the situation might be different after acquiring the lock
                if current_size < size:
                    current_size += 1
                    instance = builder()

        # Watchout: current_size can be equal to size if the previous part of
        # the function has been executed, that's why we need to check if the
        # instance is None.
        if instance is None:
            instance = local_pool.get(timeout=timeout)

        yield instance

        local_pool.put(instance)

    return pooled


# TODO: Rename this function, it's handling fulfillments not conditions
def condition_details_has_owner(condition_details, owner):
    """Check if the public_key of owner is in the condition details
    as an Ed25519Fulfillment.public_key

    Args:
        condition_details (dict): dict with condition details
        owner (str): base58 public key of owner

    Returns:
        bool: True if the public key is found in the condition details, False otherwise

    """
    if 'subconditions' in condition_details:
        result = condition_details_has_owner(condition_details['subconditions'], owner)
        if result:
            return True

    elif isinstance(condition_details, list):
        for subcondition in condition_details:
            result = condition_details_has_owner(subcondition, owner)
            if result:
                return True
    else:
        if 'public_key' in condition_details \
                and owner == condition_details['public_key']:
            return True
    return False


class Lazy:
    """Lazy objects are useful to create chains of methods to
    execute later.

    A lazy object records the methods that has been called, and
    replay them when the :py:meth:`run` method is called. Note that
    :py:meth:`run` needs an object `instance` to replay all the
    methods that have been recorded.
    """

    def __init__(self):
        """Instantiate a new Lazy object."""
        self.stack = []

    def __getattr__(self, name):
        self.stack.append(name)
        return self

    def __call__(self, *args, **kwargs):
        self.stack.append((args, kwargs))
        return self

    def __getitem__(self, key):
        self.stack.append('__getitem__')
        self.stack.append(([key], {}))
        return self

    def run(self, instance):
        """Run the recorded chain of methods on `instance`.

        Args:
            instance: an object.
        """

        last = instance

        for item in self.stack:
            if isinstance(item, str):
                last = getattr(last, item)
            else:
                last = last(*item[0], **item[1])

        self.stack = []
        return last


# Load Tendermint's public and private key from the file path
def load_node_key(path):
    with open(path) as json_data:
        priv_validator = json.load(json_data)
        priv_key = priv_validator['priv_key']['value']
        hex_private_key = key_from_base64(priv_key)
        return key_pair_from_ed25519_key(hex_private_key)


def tendermint_version_is_compatible(running_tm_ver):
    """
    Check Tendermint compatability with BigchainDB server

    :param running_tm_ver: Version number of the connected Tendermint instance
    :type running_tm_ver: str
    :return: True/False depending on the compatability with BigchainDB server
    :rtype: bool
    """

    # Splitting because version can look like this e.g. 0.22.8-40d6dc2e
    tm_ver = running_tm_ver.split('-')
    if not tm_ver:
        return False
    for ver in __tm_supported_versions__:
        if version.parse(ver) == version.parse(tm_ver[0]):
            return True
    return False
