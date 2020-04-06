# Copyright © 2020 Interplanetary Database Association e.V.,
# BigchainDB and IPDB software contributors.
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0


class BigchainDBError(Exception):
    """Base class for BigchainDB exceptions."""


class CriticalDoubleSpend(BigchainDBError):
    """Data integrity error that requires attention"""
