"""This module provides the blueprint for the votes API endpoints.

For more information please refer to the documentation: http://bigchaindb.com/http-api

We might bring back a votes API endpoint in the future, see:
https://github.com/bigchaindb/bigchaindb/issues/2037
"""

from flask import jsonify
from flask_restful import Resource
# from flask import current_app
# from flask_restful import Resource, reqparse

# from bigchaindb import backend


class VotesApi(Resource):
    def get(self):
        """API endpoint to get details about votes.

        Return:
            404 Not Found
        """
        # parser = reqparse.RequestParser()
        # parser.add_argument('block_id', type=str, required=True)

        # args = parser.parse_args(strict=True)

        # pool = current_app.config['bigchain_pool']
        # with pool() as bigchain:
        #     votes = list(backend.query.get_votes_by_block_id(bigchain.connection, args['block_id']))

        # return votes

        # Return an HTTP status code 404 Not Found, which means:
        # The requested resource could not be found but may be available in the future.

        gone = 'The votes endpoint is gone now, but it might return in the future.'
        response = jsonify({'message': gone})
        response.status_code = 404

        return response
