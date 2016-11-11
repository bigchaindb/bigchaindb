import json
import os.path


TX_SCHEMA_PATH = os.path.join(os.path.dirname(__file__), 'transaction.json')

TX_JSON_SCHEMA = json.load(open(TX_SCHEMA_PATH))
