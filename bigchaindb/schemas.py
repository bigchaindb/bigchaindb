import os
import json
from functools import lru_cache

from pkg_resources import Requirement, resource_string
import jsonschema


SCHEMAS_ROOT = 'schemas'
SCHEMAS_SUFFIX = '.json'


@lru_cache()
def load(name):
    """Load a schema from the schemas repository.
    
    Args:
        name (str): the name of the schema to load

    Returns:
        a JSON representing the schema.

    Raises:
        ``FileNotFoundError`` if the schema cannot be found.
    """
    filename = os.path.join(SCHEMAS_ROOT, name + SCHEMAS_SUFFIX)
    content = resource_string(Requirement.parse('bigchaindb'), filename)
    return json.loads(content.decode('utf8'))


def validate(data, name):
    """Validate a dictionary against a schema.
    
    Args:
        name (str): the name of the schema to use.
        data (dict): the data to validate

    Raises:
        ``jsonschema.exceptions.ValidationError`` 
    """

    jsonschema.validate(data, load(name))

