"""Code necessary for integrating with Tendermint."""

# Order is important!
# If we import core first, core will try to load BigchainDB from
# __init__ itself, causing a loop.
from bigchaindb.tendermint.lib import BigchainDB  # noqa
from bigchaindb.tendermint.core import App  # noqa
