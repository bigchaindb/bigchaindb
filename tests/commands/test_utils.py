import argparse
import pytest

from unittest.mock import patch


def test_start_raises_if_command_not_implemented():
    from bigchaindb.commands import utils
    from bigchaindb.commands.bigchain import create_parser

    parser = create_parser()

    with pytest.raises(NotImplementedError):
        # Will raise because `scope`, the third parameter,
        # doesn't contain the function `run_start`
        utils.start(parser, ['start'], {})


def test_start_raises_if_no_arguments_given():
    from bigchaindb.commands import utils
    from bigchaindb.commands.bigchain import create_parser

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


def test_mongodb_host_type():
    from bigchaindb.commands.utils import mongodb_host

    # bad port provided
    with pytest.raises(argparse.ArgumentTypeError):
        mongodb_host('localhost:11111111111')

    # no port information provided
    with pytest.raises(argparse.ArgumentTypeError):
        mongodb_host('localhost')

    # bad host provided
    with pytest.raises(argparse.ArgumentTypeError):
        mongodb_host(':27017')
