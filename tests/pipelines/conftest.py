import pytest
from unittest.mock import patch
from itertools import count

from .stepping import create_stepper


@pytest.fixture
def steps():
    stepper = create_stepper()
    with stepper.start():
        yield stepper


@pytest.fixture
def changing_timestamps():
    timestamps = (str(ts) for ts in count(1000000000)).__next__
    with patch('bigchaindb.core.gen_timestamp', timestamps):
        yield
