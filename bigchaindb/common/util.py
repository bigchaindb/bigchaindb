import time

import rapidjson


def gen_timestamp():
    """The Unix time, rounded to the nearest second.
        See https://en.wikipedia.org/wiki/Unix_time

        Returns:
            str: the Unix time
    """
    return str(round(time.time()))


def serialize(data):
    """Serialize a dict into a JSON formatted string.

        This function enforces rules like the separator and order of keys.
        This ensures that all dicts are serialized in the same way.

        This is specially important for hashing data. We need to make sure that
        everyone serializes their data in the same way so that we do not have
        hash mismatches for the same structure due to serialization
        differences.

        Args:
            data (dict): dict to serialize

        Returns:
            str: JSON formatted string

    """
    return rapidjson.dumps(data, skipkeys=False, ensure_ascii=False,
                           sort_keys=True)


def deserialize(data):
    """Deserialize a JSON formatted string into a dict.

        Args:
            data (str): JSON formatted string.

        Returns:
            dict: dict resulting from the serialization of a JSON formatted
            string.
    """
    return rapidjson.loads(data)
