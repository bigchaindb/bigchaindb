"""This module provides the blueprint for the blocks API endpoints.

For more information please refer to the documentation: http://bigchaindb.com/http-api
"""
from flask import current_app
from flask_restful import Resource, reqparse

from bigchaindb import Bigchain
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
        """API endpoint to get the related blocks for a transaction.

        Return:
            A ``list`` of ``block_id``s that contain the given transaction. The
            list may be filtered when provided a status query parameter:
            "valid", "invalid", "undecided".
        """
        parser = reqparse.RequestParser()
        parser.add_argument('transaction_id', type=str, required=True)
        parser.add_argument('status', type=str, case_sensitive=False,
                            choices=[Bigchain.BLOCK_VALID, Bigchain.BLOCK_INVALID, Bigchain.BLOCK_UNDECIDED])

        args = parser.parse_args(strict=True)
        tx_id = args['transaction_id']
        status = args['status']

        pool = current_app.config['bigchain_pool']

        with pool() as bigchain:
            block_statuses = bigchain.get_blocks_status_containing_tx(tx_id)
            blocks = [block_id for block_id, block_status in block_statuses.items()
                      if not status or block_status == status]

        return blocks
