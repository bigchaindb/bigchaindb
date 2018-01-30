"""This module provides the blueprint for some basic API endpoints.

For more information please refer to the documentation: http://bigchaindb.com/http-api
"""
import logging

from flask_restful import reqparse, Resource
from flask import current_app

from bigchaindb.backend.exceptions import OperationError
from bigchaindb.web.views.base import make_error

logger = logging.getLogger(__name__)


class MetadataApi(Resource):
    def get(self):
        """API endpoint to perform a text search on transaction metadata.

        Args:
            search (str): Text search string to query the text index
            limit (int, optional): Limit the number of returned documents.

        Return:
            A list of metadata that match the query.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('search', type=str, required=True)
        parser.add_argument('limit', type=int)
        args = parser.parse_args()

        if not args['search']:
            return make_error(400, 'text_search cannot be empty')
        if not args['limit']:
            del args['limit']

        pool = current_app.config['bigchain_pool']

        with pool() as bigchain:
            args['table'] = 'metadata'
            metadata = bigchain.text_search(**args)

        try:
            # This only works with MongoDB as the backend
            return list(metadata)
        except OperationError as e:
            return make_error(
                400,
                '({}): {}'.format(type(e).__name__, e)
            )
