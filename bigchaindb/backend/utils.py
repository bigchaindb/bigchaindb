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
