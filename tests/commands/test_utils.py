# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

import argparse
from argparse import Namespace
import logging

import pytest

from unittest.mock import patch


@pytest.fixture
def reset_bigchaindb_config(monkeypatch):
    import bigchaindb
    monkeypatch.setattr('bigchaindb.config', bigchaindb._config)


def test_input_on_stderr():
    from bigchaindb.commands.utils import input_on_stderr, _convert

    with patch('builtins.input', return_value='I love cats'):
        assert input_on_stderr() == 'I love cats'

    # input_on_stderr uses `_convert` internally, from now on we will
    # just use that function

    assert _convert('hack the planet') == 'hack the planet'
    assert _convert('42') == '42'
    assert _convert('42', default=10) == 42
    assert _convert('', default=10) == 10
    assert _convert('42', convert=int) == 42
    assert _convert('True', convert=bool) is True
    assert _convert('False', convert=bool) is False
    assert _convert('t', convert=bool) is True
    assert _convert('3.14', default=1.0) == 3.14
    assert _convert('TrUe', default=False) is True

    with pytest.raises(ValueError):
        assert _convert('TRVE', default=False)

    with pytest.raises(ValueError):
        assert _convert('ಠ_ಠ', convert=int)


@pytest.mark.usefixtures('ignore_local_config_file', 'reset_bigchaindb_config')
def test_configure_bigchaindb_configures_bigchaindb():
    from bigchaindb.commands.utils import configure_bigchaindb
    from bigchaindb.config_utils import is_configured
    assert not is_configured()

    @configure_bigchaindb
    def test_configure(args):
        assert is_configured()

    args = Namespace(config=None)
    test_configure(args)


@pytest.mark.usefixtures('ignore_local_config_file',
                         'reset_bigchaindb_config',
                         'reset_logging_config')
@pytest.mark.parametrize('log_level', tuple(map(
    logging.getLevelName,
    (logging.DEBUG,
     logging.INFO,
     logging.WARNING,
     logging.ERROR,
     logging.CRITICAL)
)))
def test_configure_bigchaindb_logging(log_level):
    # TODO: See following comment:
    # This is a dirty test. If a test *preceding* this test makes use of the logger, and then another test *after* this
    # test also makes use of the logger, somehow we get logger.disabled == True, and the later test fails. We need to
    # either engineer this somehow to leave the test env in the same state as it finds it, or make an assessment
    # whether or not we even need this test, and potentially just remove it.

    from bigchaindb.commands.utils import configure_bigchaindb

    @configure_bigchaindb
    def test_configure_logger(args):
        pass

    args = Namespace(config=None, log_level=log_level)
    test_configure_logger(args)
    from bigchaindb import config
    assert config['log']['level_console'] == log_level
    assert config['log']['level_logfile'] == log_level


def test_start_raises_if_command_not_implemented():
    from bigchaindb.commands import utils
    from bigchaindb.commands.bigchaindb import create_parser

    parser = create_parser()

    with pytest.raises(NotImplementedError):
        # Will raise because `scope`, the third parameter,
        # doesn't contain the function `run_start`
        utils.start(parser, ['start'], {})


def test_start_raises_if_no_arguments_given():
    from bigchaindb.commands import utils
    from bigchaindb.commands.bigchaindb import create_parser

    parser = create_parser()

    with pytest.raises(SystemExit):
        utils.start(parser, [], {})


@patch('multiprocessing.cpu_count', return_value=42)
def test_start_sets_multiprocess_var_based_on_cli_args(mock_cpu_count):
    from bigchaindb.commands import utils

    def run_mp_arg_test(args):
        return args

    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers(title='Commands',
                                      dest='command')
    mp_arg_test_parser = subparser.add_parser('mp_arg_test')
    mp_arg_test_parser.add_argument('-m', '--multiprocess',
                                    nargs='?',
                                    type=int,
                                    default=False)

    scope = {'run_mp_arg_test': run_mp_arg_test}
    assert utils.start(parser, ['mp_arg_test'], scope).multiprocess == 1
    assert utils.start(parser, ['mp_arg_test', '--multiprocess'], scope).multiprocess == 42
