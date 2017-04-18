"""This module provides the blueprint for the votes API endpoints.

For more information please refer to the documentation: http://bigchaindb.com/http-api
"""
from flask import current_app
from flask_restful import Resource, reqparse

from bigchaindb import backend


class VotesApi(Resource):
    def get(self):
        """API endpoint to get details about votes on a block.

        Return:
            A list of votes voting for a block with ID ``block_id``.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('block_id', type=str, required=True)

        args = parser.parse_args(strict=True)

        pool = current_app.config['bigchain_pool']
        with pool() as bigchain:
            votes = list(backend.query.get_votes_by_block_id(bigchain.connection, args['block_id']))

        return votes
