"""This module provides the blueprint for the votes API endpoints.

For more information please refer to the documentation on ReadTheDocs:
 - https://docs.bigchaindb.com/projects/server/en/latest/drivers-clients/
   http-client-server-api.html
"""
from flask import current_app
from flask_restful import Resource, reqparse

from bigchaindb import backend
from bigchaindb.web.views.base import make_error


class VotesApi(Resource):
    def get(self):
        """API endpoint to get details about votes on a block.

        Return:
            A list of votes voting for a block with ID ``block_id``.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('block_id', type=str)

        args = parser.parse_args(strict=True)

        if sum(arg is not None for arg in args.values()) != 1:
            return make_error(400, "Provide the block_id query parameter.")

        pool = current_app.config['bigchain_pool']
        votes = []

        with pool() as bigchain:
            if args['block_id']:
                votes = list(backend.query.get_votes_by_block_id(bigchain.connection, args['block_id']))

        return votes
