"""This module provides the blueprint for some basic API endpoints.

For more information please refer to the documentation on ReadTheDocs:
 - https://bigchaindb.readthedocs.io/en/latest/drivers-clients/http-client-server-api.html
"""
from flask import current_app, request, Blueprint
from flask_restful import Resource, Api

import bigchaindb
from bigchaindb import util
from bigchaindb.web.views.base import make_error


block_views = Blueprint('block_views', __name__)
block_api = Api(block_views)


# Unfortunately I cannot find a reference to this decorator.
# This answer on SO is quite useful tho:
# - http://stackoverflow.com/a/13432373/597097
@block_views.record
def record(state):
    """This function checks if the blueprint can be initialized
    with the provided state."""

    bigchain_pool = state.app.config.get('bigchain_pool')
    monitor = state.app.config.get('monitor')

    if bigchain_pool is None:
        raise Exception('This blueprint expects you to provide '
                        'a pool of Bigchain instances called `bigchain_pool`')

    if monitor is None:
        raise ValueError('This blueprint expects you to provide '
                         'a monitor instance to record system '
                         'performance.')


class BlockApi(Resource):
    def get(self, block_id):
        """API endpoint to get details about a block.

        Args:
            block_id (str): the id of the block.

        Return:
            A dict containing the data about the block.
        """
        pool = current_app.config['bigchain_pool']

        with pool() as bigchain:
            tx = bigchain.get_block(block_id)

        if not tx:
            return make_error(404)

        return tx


block_api.add_resource(BlockApi, '/blocks/<string:tx_id>', strict_slashes=False)
