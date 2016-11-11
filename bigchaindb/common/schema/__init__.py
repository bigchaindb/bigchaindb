import yaml
import os.path


TX_SCHEMA_PATH = os.path.join(os.path.dirname(__file__), 'transaction.yaml')

TX_JSON_SCHEMA = yaml.load(open(TX_SCHEMA_PATH).read())
