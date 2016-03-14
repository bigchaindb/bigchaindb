# BigchainDB Consensus Plugins

BigchainDB has a pluggable block/transaction validation architecture. The default consensus rules can be extended or replaced entirely.


## Installing a plugin

Plugins can be installed via pip!

```bash
$ pip install bigchaindb-plugin-demo
```

Or using setuptools:

```bash
$ cd bigchaindb-plugin-demo/
$ python setup.py install # (or develop)
```

To activate your plugin, you can either set the `consensus_plugin` field in your config file (usually `~/.bigchaindb`) or by setting the `BIGCHAIN_CONSENSUS_PLUGIN` environement variable to the name of your plugin (see the section on [Packaging a plugin](#packaging-a-plugin) for more about plugin names).


## Plugin API

BigchainDB's [current plugin API](../../bigchaindb/consensus.py) exposes five functions in an `AbstractConsensusRules` class:

```python
validate_transaction(bigchain, transaction)
validate_block(bigchain, block)
create_transaction(*args, **kwargs)
sign_transaction(transaction, *args, **kwargs)
verify_signature(transaction)
```

Together, these functions are sufficient for most customizations. For example:
- Replace the crypto-system with one your hardware can accelerate
- Re-implement an existing protocol
- Delegate validation to another application
- etc...


## Extending BigchainDB behavior

A default installation of BigchainDB will use the rules in the `BaseConsensusRules` class. If you only need to modify this behavior slightly, you can inherit from that class and call `super()` in any methods you change, so long as the return values remain the same.

Here's a quick example of a plugin that adds nonsense rules:

```python
from bigchaindb.consensus import BaseConsensusRules

class SillyConsensusRules(BaseConsensusRules):

    @staticmethod
    def validate_transaction(bigchain, transaction):
        transaction = super().validate_transaction(bigchain, transaction)
        # I only like transactions whose timestamps are even.
        if transaction['transaction']['timestamp'] % 2 != 0:
            raise StandardError("Odd... very odd indeed.")
        return transaction

    @staticmethod
    def validate_block(bigchain, block):
        block = super().validate_block(bigchain, block)
        # I don't trust Alice, I think she's shady.
        if block['block']['node_pubkey'] == '<ALICE_PUBKEY>':
            raise StandardError("Alice is shady, everybody ignore her blocks!")
       return block
```


## Packaging a plugin

BigchainDB uses [setuptool's entry_point](https://pythonhosted.org/setuptools/setuptools.html) system to provide the plugin functionality. Any custom plugin needs to add this section to the `setup()` call in their `setup.py`:

```python
entry_points={
    'bigchaindb.consensus': [
        'PLUGIN_NAME=package.module:ConsensusRulesClass'
    ]
},
```
