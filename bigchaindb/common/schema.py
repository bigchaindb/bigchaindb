""" Schema definitions for BigchainDB data structure """

def nullable(data):
    """ Describe optional data """
    return {"anyOf": [data, {"type": "null"}]}


class SchemaObject(object):
    @classmethod
    def to_json_schema(cls):
        pass


class InnerTransaction(SchemaObject):
    """
    An InnerTransaction contains the bulk of the information of a transaction.
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

    timestamp = {
        "type": "string",
        "pattern": "\\d{10}\\.\\d{6}"
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

    required = ["fulfillments", "conditions", "operation", "timestamp", "data"]


class Transaction(object):
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
    id = {"$ref": "#/definitions/sha3_hexdigest"}
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

    transaction = InnerTransaction.to_json_schema()


__all__ = ['Transaction', 'InnerTransaction']
