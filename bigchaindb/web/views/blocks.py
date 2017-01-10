"""This module provides the blueprint for the blocks API endpoints.

For more information please refer to the documentation on ReadTheDocs:
 - https://docs.bigchaindb.com/projects/server/en/latest/drivers-clients/
   http-client-server-api.html
"""
from flask import current_app
from flask_restful import Resource, reqparse

from bigchaindb.web.views.base import make_error


class BlockApi(Resource):
    def get(self, block_id):
        """API endpoint to get details about a block.

        Args:
            block_id (str): the id of the block.

        Return:
            A JSON string containing the data about the block.
        """

        pool = current_app.config['bigchain_pool']

        with pool() as bigchain:
            block = bigchain.get_block(block_id=block_id)

        if not block:
            return make_error(404)

        return block


class BlockListApi(Resource):
    def get(self):
        """API endpoint to get the related blocks and statuses of a transaction.

        Return:
            A ``dict`` in the format ``{'block_id': <status>}``, where
            ``<status>`` is one of "valid", "invalid", "undecided", "backlog".
            It's possible to return multiple keys of 'block_id'.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('tx_id', type=str)

        args = parser.parse_args(strict=True)

        if sum(arg is not None for arg in args.values()) != 1:
            return make_error(400, "Provide exactly one query parameter. Choices are: block_id, tx_id")

        pool = current_app.config['bigchain_pool']
        blocks = None

        with pool() as bigchain:
            if args['tx_id']:
                blocks = bigchain.get_blocks_status_containing_tx(args['tx_id'])

        if not blocks:
            return make_error(404)

        return blocks
