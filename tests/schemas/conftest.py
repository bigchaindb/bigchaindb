import json
import os

import pytest



@pytest.fixture
def transaction_schema():
    my_dir = os.path.dirname(os.path.realpath(__file__))

    schema_path = os.path.join(my_dir, '..', '..', 'schemas',
                               'transaction-schema.json')

    with open(schema_path) as f:
        return json.load(f)

