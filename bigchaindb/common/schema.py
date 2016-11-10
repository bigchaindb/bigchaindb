"""
Schema definitions for BigchainDB data structure.

Schema definitons are defined here in classes which are then translated
into Json Schema (http://json-schema.org/). The classes are used for
readability and to make documenting easier.
"""


def nullable(data):
    """ Describe optional data """
    return {"anyOf": [data, {"type": "null"}]}


class SchemaObject(object):
    """ Class to represent a Schema Object """
    @classmethod
    def to_json_schema(cls):
        """
        Convert a SchemaObject into Json Schema
        """
        out = {
            'type': 'object'
        }
        for k, v in cls.__dict__.items():
            if k.startswith('__'):
                continue
            if isinstance(v, type) and issubclass(v, SchemaObject):
                v = v.to_json_schema()
            if k in ['_definitions', '_required']:
                out[k[1:]] = v
            else:
                out.setdefault('properties', {})[k] = v
        return out


class TransactionBody(SchemaObject):
    """
    A TransactionBody contains the body of the information of a transaction.
    """
    operation = {
        "type": "string",
        "enum": ["CREATE", "TRANSFER"]
    }
    """
    A "CREATE" transaction creates a new asset and has no inputs.

    A "TRANSFER" transaction redefines ownership of a whole or part of an asset
    and has inputs.
    """

    conditions = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "new_owners": {
                    "$ref": "#/definitions/owners_list"
                },
                "condition": {
                    "type": "object",
                    "properties": {
                        "details": {
                            "type": "object"
                        },
                        "uri": {
                            "type": "string"
                        }
                    },
                    "required": ["uri"]
                },
                "cid": {"type": "integer"}
            },
            "required": ["new_owners", "condition", "cid"]
        }
    }
    """
    Conditions are the outputs of a transaction, a successive transaction may
    spend them by providing corresponding fulfillments.
    """

    fulfillments = {
        "type": "array",
        "items": {
            "current_owners": {
                "$ref": "#/definitions/owners_list"
            },
            "input": nullable({
                "$ref": "#/definitions/sha3_hexdigest"
            }),
            "fulfillment": {
                "type": "string"
            },
            "fid": {
                "type": "integer"
            }
        },
        "required": ["current_owners", "input", "fulfillment", "fid"]
    }
    """
    Fulfillments provide inputs to a transaction by fulfilling conditions of
    previous transactions.
    """

    timestamp = {
        "type": "string",
        "pattern": "\\d{10}"
    }

    metadata = nullable({
        "type": "object",
        "properties": {
            "hash": {"$ref": "#/definitions/sha3_hexdigest"},
            "payload": {
                "type": "object"
            }
        },
        "required": ["hash", "payload"]
    })

    _required = ["fulfillments", "conditions", "operation",
                 "timestamp", "metadata"]


class Transaction(SchemaObject):
    """
    A Transaction is an operation to create or transfer an asset.
    """
    _definitions = {
        "sha3_hexdigest": {
            "type": "string",
            "pattern": "[0-9a-f]{64}"
        },
        "base58": {
            "type": "string",
            "pattern": "[1-9a-zA-Z^OIl]{43,44}"
        },
        "owners_list": nullable({
            "type": "array",
            "items": {"$ref": "#/DEFINITIONS/base58"}
        }),
    }

    id = {"$ref": "#/definitions/sha3_hexdigest"}  # noqa
    """
    Transaction ID is a sha3 hash of the JSON dump of the transaction,
    with object keys in alphabetical order.
    """

    version = {
        "type": "integer",
        "minimum": 1,
        "maximum": 1
    }
    """
    Transaction is currently targeting version 1, but still somewhat in flux.
    """

    transaction = TransactionBody
    """
    The body of the transaction. The body of the transaction is not at top level
    so that the ID, which is a hash of the body, does not depend on itself.
    """


TRANSACTION_JSON_SCHEMA = Transaction.to_json_schema()
