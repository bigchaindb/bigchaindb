from collections import OrderedDict
import os.path

import yaml


def ordered_load(stream):
    class OrderedLoader(yaml.SafeLoader):
        pass

    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return OrderedDict(loader.construct_pairs(node))
    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)
    return yaml.load(stream, OrderedLoader)


TX_SCHEMA_PATH = os.path.join(os.path.dirname(__file__), 'transaction.yaml')
TX_SCHEMA_DATA = open(TX_SCHEMA_PATH).read()
TX_SCHEMA = yaml.load(TX_SCHEMA_DATA, yaml.SafeLoader)
TX_SCHEMA_ORDERED = ordered_load(TX_SCHEMA_DATA)
