# Copyright © 2020 Interplanetary Database Association e.V.,
# BigchainDB and IPDB software contributors.
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

import bigchaindb


class ModuleDispatchRegistrationError(Exception):
    """Raised when there is a problem registering dispatched functions for a
    module
    """


def module_dispatch_registrar(module):
    def dispatch_wrapper(obj_type):
        def wrapper(func):
            func_name = func.__name__
            try:
                dispatch_registrar = getattr(module, func_name)
                return dispatch_registrar.register(obj_type)(func)
            except AttributeError as ex:
                raise ModuleDispatchRegistrationError(
                    ('`{module}` does not contain a single-dispatchable '
                     'function named `{func}`. The module being registered '
                     'was not implemented correctly!').format(
                        func=func_name, module=module.__name__)) from ex

        return wrapper

    return dispatch_wrapper


def get_bigchaindb_config_value(key, default_value=None):
    return bigchaindb.config['database'].get(key, default_value)


def get_bigchaindb_config_value_or_key_error(key):
    return bigchaindb.config['database'][key]
