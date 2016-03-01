"""Utils to configure Bigchain.

By calling `file_config`, the global configuration (stored in
`bigchain.config`) will be updated with the values contained in the
configuration file.

Note that there is a precedence in reading configuration values:
 - [not yet] command line;
 - local config file;
 - environment vars;
 - default config file (contained in `bigchain.__init__`).
"""

import os
import copy
import json
import logging
import collections

from pkg_resources import iter_entry_points

import bigchaindb

logger = logging.getLogger(__name__)
CONFIG_DEFAULT_PATH = os.environ.setdefault(
    'BIGCHAINDB_CONFIG_PATH',
    os.path.join(os.path.expanduser('~'), '.bigchaindb'),
)


# Thanks Alex <3
# http://stackoverflow.com/a/3233356/597097
def update(d, u):
    """Recursively update a mapping."""
    for k, v in u.items():
        if isinstance(v, collections.Mapping):
            r = update(d.get(k, {}), v)
            d[k] = r
        else:
            d[k] = u[k]
    return d


def file_config(filename=None):
    """Read a configuration file and merge it with the default configuration.

    Args:
        filename (str): the JSON file with the configuration. Defaults to ``None``.
            If ``None``, the HOME of the current user and the string ``.bigchaindb`` will be used.

    Note:
        The function merges the values in ``filename`` with the **default configuration**,
        so any update made to ``bigchaindb.config`` will be lost.
    """
    if not filename:
        filename = CONFIG_DEFAULT_PATH

    with open(filename) as f:
        newconfig = json.load(f)

    dict_config(newconfig)
    logger.info('Configuration loaded from `{}`'.format(filename))


def dict_config(newconfig):
    """Merge the provided configuration with the default one.

    Args:
        newconfig (dict): a dictionary with the configuration to load.

    Note:
        The function merges ``newconfig`` with the **default configuration**, so any
        update made to ``bigchaindb.config`` will be lost.
    """
    bigchaindb.config = copy.deepcopy(bigchaindb._config)
    update(bigchaindb.config, newconfig)
    bigchaindb.config['CONFIGURED'] = True


def write_config(newconfig, filename=None):
    """Write the provided configuration to a specific location.

    Args:
        newconfig (dict): a dictionary with the configuration to load.
        filename (str): the name of the file that will store the new configuration. Defaults to ``None``.
            If ``None``, the HOME of the current user and the string ``.bigchaindb`` will be used.
    """
    if not filename:
        filename = CONFIG_DEFAULT_PATH

    with open(filename, 'w') as f:
        json.dump(newconfig, f)


def autoconfigure():
    """Run ``file_config`` if the module has not been initialized.
    """
    if bigchaindb.config.get('CONFIGURED'):
        return
    try:
        file_config()
    except FileNotFoundError:
        logger.warning('Cannot find your config file. Run `bigchaindb configure` to create one')


def get_plugins(plugin_names):
    if not plugin_names:
        plugin_names = bigchaindb.config.get('consensus_plugins', [])

    plugins = []

    # It's important to maintain plugin ordering as stated in the config file.
    # e.g. Expensive validation tasks should happen after cheap ones.
    #
    # TODO: We might want to add some sort of priority system, but for now we
    #       simply assume everything in a given plugin is designed to run at the
    #       same time.
    for name in plugin_names:
        for entry_point in iter_entry_points('bigchaindb.plugins', name):
            plugins.append(entry_point.load())

    return plugins
