import pytest

from .stepping import create_stepper


@pytest.fixture
def steps():
    stepper = create_stepper()
    with stepper.start():
        yield stepper
