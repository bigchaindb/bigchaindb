# Copyright © 2020 Interplanetary Database Association e.V.,
# BigchainDB and IPDB software contributors.
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

import time
import re
import rapidjson

import bigchaindb
from bigchaindb.common.exceptions import ValidationError


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


def validate_txn_obj(obj_name, obj, key, validation_fun):
    """Validate value of `key` in `obj` using `validation_fun`.

        Args:
            obj_name (str): name for `obj` being validated.
            obj (dict): dictionary object.
            key (str): key to be validated in `obj`.
            validation_fun (function): function used to validate the value
            of `key`.

        Returns:
            None: indicates validation successful

        Raises:
            ValidationError: `validation_fun` will raise exception on failure
    """
    backend = bigchaindb.config['database']['backend']

    if backend == 'localmongodb':
        data = obj.get(key, {})
        if isinstance(data, dict):
            validate_all_keys_in_obj(obj_name, data, validation_fun)
        elif isinstance(data, list):
            validate_all_items_in_list(obj_name, data, validation_fun)


def validate_all_items_in_list(obj_name, data, validation_fun):
    for item in data:
        if isinstance(item, dict):
            validate_all_keys_in_obj(obj_name, item, validation_fun)
        elif isinstance(item, list):
            validate_all_items_in_list(obj_name, item, validation_fun)


def validate_all_keys_in_obj(obj_name, obj, validation_fun):
    """Validate all (nested) keys in `obj` by using `validation_fun`.

        Args:
            obj_name (str): name for `obj` being validated.
            obj (dict): dictionary object.
            validation_fun (function): function used to validate the value
            of `key`.

        Returns:
            None: indicates validation successful

        Raises:
            ValidationError: `validation_fun` will raise this error on failure
    """
    for key, value in obj.items():
        validation_fun(obj_name, key)
        if isinstance(value, dict):
            validate_all_keys_in_obj(obj_name, value, validation_fun)
        elif isinstance(value, list):
            validate_all_items_in_list(obj_name, value, validation_fun)


def validate_all_values_for_key_in_obj(obj, key, validation_fun):
    """Validate value for all (nested) occurrence  of `key` in `obj`
       using `validation_fun`.

        Args:
            obj (dict): dictionary object.
            key (str): key whose value is to be validated.
            validation_fun (function): function used to validate the value
            of `key`.

        Raises:
            ValidationError: `validation_fun` will raise this error on failure
    """
    for vkey, value in obj.items():
        if vkey == key:
            validation_fun(value)
        elif isinstance(value, dict):
            validate_all_values_for_key_in_obj(value, key, validation_fun)
        elif isinstance(value, list):
            validate_all_values_for_key_in_list(value, key, validation_fun)


def validate_all_values_for_key_in_list(input_list, key, validation_fun):
    for item in input_list:
        if isinstance(item, dict):
            validate_all_values_for_key_in_obj(item, key, validation_fun)
        elif isinstance(item, list):
            validate_all_values_for_key_in_list(item, key, validation_fun)


def validate_key(obj_name, key):
    """Check if `key` contains ".", "$" or null characters.

       https://docs.mongodb.com/manual/reference/limits/#Restrictions-on-Field-Names

        Args:
            obj_name (str): object name to use when raising exception
            key (str): key to validated

        Returns:
            None: validation successful

        Raises:
            ValidationError: will raise exception in case of regex match.
    """
    if re.search(r'^[$]|\.|\x00', key):
        error_str = ('Invalid key name "{}" in {} object. The '
                     'key name cannot contain characters '
                     '".", "$" or null characters').format(key, obj_name)
        raise ValidationError(error_str)
