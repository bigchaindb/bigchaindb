"""Utils for reading and setting configuration settings.

The value of each BigchainDB Server configuration setting is
determined according to the following rules:

* If it's set by an environment variable, then use that value
* Otherwise, if it's set in a local config file, then use that
  value
* Otherwise, use the default value (contained in
  ``bigchaindb.__init__``)
"""


import os
import copy
import json
import logging
import collections
from functools import lru_cache

from pkg_resources import iter_entry_points, ResolutionError

from bigchaindb.common import exceptions

import bigchaindb

from bigchaindb.consensus import BaseConsensusRules

# TODO: move this to a proper configuration file for logging
logging.getLogger('requests').setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

CONFIG_DEFAULT_PATH = os.environ.setdefault(
    'BIGCHAINDB_CONFIG_PATH',
    os.path.join(os.path.expanduser('~'), '.bigchaindb'),
)

CONFIG_PREFIX = 'BIGCHAINDB'
CONFIG_SEP = '_'


def map_leafs(func, mapping):
    """Map a function to the leafs of a mapping."""

    def _inner(mapping, path=None):
        if path is None:
            path = []

        for key, val in mapping.items():
            if isinstance(val, collections.Mapping):
                _inner(val, path + [key])
            else:
                mapping[key] = func(val, path=path+[key])

        return mapping

    return _inner(copy.deepcopy(mapping))


# Thanks Alex <3
# http://stackoverflow.com/a/3233356/597097
def update(d, u):
    """Recursively update a mapping (i.e. a dict, list, set, or tuple).

    Conceptually, d and u are two sets trees (with nodes and edges).
    This function goes through all the nodes of u. For each node in u,
    if d doesn't have that node yet, then this function adds the node from u,
    otherwise this function overwrites the node already in d with u's node.

    Args:
        d (mapping): The mapping to overwrite and add to.
        u (mapping): The mapping to read for changes.

    Returns:
        mapping: An updated version of d (updated by u).
    """
    for k, v in u.items():
        if isinstance(v, collections.Mapping):
            r = update(d.get(k, {}), v)
            d[k] = r
        else:
            d[k] = u[k]
    return d


def file_config(filename=None):
    """Returns the config values found in a configuration file.

    Args:
        filename (str): the JSON file with the configuration values.
            If ``None``, CONFIG_DEFAULT_PATH will be used.

    Returns:
        dict: The config values in the specified config file (or the
              file at CONFIG_DEFAULT_PATH, if filename == None)
    """
    logger.debug('On entry into file_config(), filename = {}'.format(filename))

    if filename is None:
        filename = CONFIG_DEFAULT_PATH

    logger.debug('file_config() will try to open `{}`'.format(filename))
    with open(filename) as f:
        try:
            config = json.load(f)
        except ValueError as err:
            raise exceptions.ConfigurationError(
                'Failed to parse the JSON configuration from `{}`, {}'.format(filename, err)
            )

        logger.info('Configuration loaded from `{}`'.format(filename))

    return config


def env_config(config):
    """Return a new configuration with the values found in the environment.

    The function recursively iterates over the config, checking if there is
    a matching env variable. If an env variable is found, the func updates
    the configuration with that value.

    The name of the env variable is built combining a prefix (``BIGCHAINDB``)
    with the path to the value. If the ``config`` in input is:
    ``{'database': {'host': 'localhost'}}``
    this function will try to read the env variable ``BIGCHAINDB_DATABASE_HOST``.
    """

    def load_from_env(value, path):
        var_name = CONFIG_SEP.join([CONFIG_PREFIX] + list(map(lambda s: s.upper(), path)))

        return os.environ.get(var_name, value)

    return map_leafs(load_from_env, config)


def update_types(config, reference, list_sep=':'):
    """Return a new configuration where all the values types
    are aligned with the ones in the default configuration
    """

    def _coerce(current, value):
        # Coerce a value to the `current` type.
        try:
            # First we try to apply current to the value, since it
            # might be a function
            return current(value)
        except TypeError:
            # Then we check if current is a list AND if the value
            # is a string.
            if isinstance(current, list) and isinstance(value, str):
                # If so, we use the colon as the separator
                return value.split(list_sep)

            try:
                # If we are here, we should try to apply the type
                # of `current` to the value
                return type(current)(value)
            except TypeError:
                # Worst case scenario we return the value itself.
                return value

    def _update_type(value, path):
        current = reference

        for elem in path:
            try:
                current = current[elem]
            except KeyError:
                return value

        return _coerce(current, value)

    return map_leafs(_update_type, config)


def set_config(config):
    """Set bigchaindb.config equal to the default config dict,
    then update that with whatever is in the provided config dict,
    and then set bigchaindb.config['CONFIGURED'] = True

    Args:
        config (dict): the config dict to read for changes
                       to the default config

    Note:
        Any previous changes made to ``bigchaindb.config`` will be lost.
    """
    # Deep copy the default config into bigchaindb.config
    bigchaindb.config = copy.deepcopy(bigchaindb._config)
    # Update the default config with whatever is in the passed config
    update(bigchaindb.config, update_types(config, bigchaindb.config))
    bigchaindb.config['CONFIGURED'] = True


def update_config(config):
    """Update bigchaindb.config with whatever is in the provided config dict,
    and then set bigchaindb.config['CONFIGURED'] = True

    Args:
        config (dict): the config dict to read for changes
                       to the default config
    """

    # Update the default config with whatever is in the passed config
    update(bigchaindb.config, update_types(config, bigchaindb.config))
    bigchaindb.config['CONFIGURED'] = True


def write_config(config, filename=None):
    """Write the provided configuration to a specific location.

    Args:
        config (dict): a dictionary with the configuration to load.
        filename (str): the name of the file that will store the new configuration. Defaults to ``None``.
            If ``None``, the HOME of the current user and the string ``.bigchaindb`` will be used.
    """
    if not filename:
        filename = CONFIG_DEFAULT_PATH

    with open(filename, 'w') as f:
        json.dump(config, f, indent=4)


def is_configured():
    return bool(bigchaindb.config.get('CONFIGURED'))


def autoconfigure(filename=None, config=None, force=False):
    """Run ``file_config`` and ``env_config`` if the module has not
    been initialized.
    """
    if not force and is_configured():
        logger.debug('System already configured, skipping autoconfiguration')
        return

    # start with the current configuration
    newconfig = bigchaindb.config

    # update configuration from file
    try:
        newconfig = update(newconfig, file_config(filename=filename))
    except FileNotFoundError as e:
        if filename:
            raise
        else:
            logger.info('Cannot find config file `%s`.' % e.filename)

    # override configuration with env variables
    newconfig = env_config(newconfig)
    if config:
        newconfig = update(newconfig, config)
    set_config(newconfig)  # sets bigchaindb.config


@lru_cache()
def load_consensus_plugin(name=None):
    """Find and load the chosen consensus plugin.

    Args:
        name (string): the name of the entry_point, as advertised in the
            setup.py of the providing package.

    Returns:
        an uninstantiated subclass of ``bigchaindb.consensus.AbstractConsensusRules``
    """
    if not name:
        return BaseConsensusRules

    # TODO: This will return the first plugin with group `bigchaindb.consensus`
    #       and name `name` in the active WorkingSet.
    #       We should probably support Requirements specs in the config, e.g.
    #       consensus_plugin: 'my-plugin-package==0.0.1;default'
    plugin = None
    for entry_point in iter_entry_points('bigchaindb.consensus', name):
        plugin = entry_point.load()

    # No matching entry_point found
    if not plugin:
        raise ResolutionError(
            'No plugin found in group `bigchaindb.consensus` with name `{}`'.
            format(name))

    # Is this strictness desireable?
    # It will probably reduce developer headaches in the wild.
    if not issubclass(plugin, (BaseConsensusRules,)):
        raise TypeError('object of type "{}" does not implement `bigchaindb.'
                        'consensus.BaseConsensusRules`'.format(type(plugin)))

    return plugin


def load_events_plugins(names=None):
    plugins = []

    if names is None:
        return plugins

    for name in names:
        for entry_point in iter_entry_points('bigchaindb.events', name):
            plugins.append((name, entry_point.load()))

    return plugins
