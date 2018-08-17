# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

"""API routes definition"""
from flask_restful import Api
from bigchaindb.web.views import (
    assets,
    metadata,
    blocks,
    info,
    transactions as tx,
    outputs,
    validators,
)


def add_routes(app):
    """Add the routes to an app"""
    for (prefix, routes) in API_SECTIONS:
        api = Api(app, prefix=prefix)
        for ((pattern, resource, *args), kwargs) in routes:
            kwargs.setdefault('strict_slashes', False)
            api.add_resource(resource, pattern, *args, **kwargs)


def r(*args, **kwargs):
    return (args, kwargs)


ROUTES_API_V1 = [
    r('/', info.ApiV1Index),
    r('assets/', assets.AssetListApi),
    r('metadata/', metadata.MetadataApi),
    r('blocks/<int:block_id>', blocks.BlockApi),
    r('blocks/', blocks.BlockListApi),
    r('transactions/<string:tx_id>', tx.TransactionApi),
    r('transactions', tx.TransactionListApi),
    r('outputs/', outputs.OutputListApi),
    r('validators/', validators.ValidatorsApi),
]


API_SECTIONS = [
    (None, [r('/', info.RootIndex)]),
    ('/api/v1/', ROUTES_API_V1),
]
