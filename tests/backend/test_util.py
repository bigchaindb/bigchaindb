import pytest

from types import ModuleType


@pytest.fixture
def mock_module():
    return ModuleType('mock_module')


def test_module_dispatch_registers(mock_module):
    from functools import singledispatch
    from bigchaindb.backend.utils import make_module_dispatch_registrar

    @singledispatch
    def dispatcher(t):
        pass
    mock_module.dispatched = dispatcher
    mock_dispatch = make_module_dispatch_registrar(mock_module)

    @mock_dispatch(str)
    def dispatched(t):
        pass

    assert mock_module.dispatched.registry[str] == dispatched


def test_module_dispatch_dispatches(mock_module):
    from functools import singledispatch
    from bigchaindb.backend.utils import make_module_dispatch_registrar

    @singledispatch
    def dispatcher(t):
        return False
    mock_module.dispatched = dispatcher
    mock_dispatch = make_module_dispatch_registrar(mock_module)

    @mock_dispatch(str)
    def dispatched(t):
        return True

    assert mock_module.dispatched(1) is False  # Goes to dispatcher()
    assert mock_module.dispatched('1') is True  # Goes to dispatched()


def test_module_dispatch_errors_on_missing_func(mock_module):
    from bigchaindb.backend.utils import (
        make_module_dispatch_registrar,
        BackendModuleDispatchRegisterError,
    )
    mock_dispatch = make_module_dispatch_registrar(mock_module)

    with pytest.raises(BackendModuleDispatchRegisterError):
        @mock_dispatch(str)
        def dispatched():
            pass


def test_module_dispatch_errors_on_non_dispatchable_func(mock_module):
    from bigchaindb.backend.utils import (
        make_module_dispatch_registrar,
        BackendModuleDispatchRegisterError,
    )

    def dispatcher():
        pass
    mock_module.dispatched = dispatcher
    mock_dispatch = make_module_dispatch_registrar(mock_module)

    with pytest.raises(BackendModuleDispatchRegisterError):
        @mock_dispatch(str)
        def dispatched():
            pass
