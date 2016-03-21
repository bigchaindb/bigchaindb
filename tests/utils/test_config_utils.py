import copy

import pytest

import bigchaindb
from bigchaindb import exceptions


ORIGINAL_CONFIG = copy.deepcopy(bigchaindb._config)


@pytest.fixture(scope='function', autouse=True)
def clean_config(monkeypatch):
    monkeypatch.setattr('bigchaindb.config', copy.deepcopy(ORIGINAL_CONFIG))


def test_bigchain_instance_is_initialized_when_conf_provided():
    from bigchaindb import config_utils
    assert 'CONFIGURED' not in bigchaindb.config

    config_utils.dict_config({'keypair': {'public': 'a', 'private': 'b'}})

    assert bigchaindb.config['CONFIGURED'] is True
    b = bigchaindb.Bigchain()

    assert b.me
    assert b.me_private


def test_bigchain_instance_raises_when_not_configured(monkeypatch):
    from bigchaindb import config_utils
    assert 'CONFIGURED' not in bigchaindb.config

    # We need to disable ``bigchaindb.config_utils.autoconfigure`` to avoid reading
    # from existing configurations
    monkeypatch.setattr(config_utils, 'autoconfigure', lambda: 0)

    with pytest.raises(exceptions.KeypairNotFoundException):
        bigchaindb.Bigchain()


def test_load_consensus_plugin_loads_default_rules_without_name():
    from bigchaindb import config_utils
    from bigchaindb.consensus import BaseConsensusRules

    assert config_utils.load_consensus_plugin() == BaseConsensusRules


def test_load_consensus_plugin_raises_with_unknown_name():
    from pkg_resources import ResolutionError
    from bigchaindb import config_utils

    with pytest.raises(ResolutionError):
        config_utils.load_consensus_plugin('bogus')


def test_load_consensus_plugin_raises_with_invalid_subclass(monkeypatch):
    # Monkeypatch entry_point.load to return something other than a
    # ConsensusRules instance
    from bigchaindb import config_utils
    monkeypatch.setattr(config_utils,
                        'iter_entry_points',
                        lambda *args: [ type('entry_point',
                                             (object),
                                             {'load': lambda: object}) ])

    with pytest.raises(TypeError):
        config_utils.load_consensus_plugin()
