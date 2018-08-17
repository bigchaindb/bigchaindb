# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

"""Generic backend database interfaces expected by BigchainDB.

The interfaces in this module allow BigchainDB to be agnostic about its
database backend. One can configure BigchainDB to use different databases as
its data store by setting the ``database.backend`` property in the
configuration or the ``BIGCHAINDB_DATABASE_BACKEND`` environment variable.
"""

# Include the backend interfaces
from bigchaindb.backend import schema, query  # noqa

from bigchaindb.backend.connection import connect  # noqa
