"""This module provides the blueprint for some basic API endpoints.

For more information please refer to the documentation: http://bigchaindb.com/http-api
"""
import logging

from flask_restful import reqparse, Resource

from bigchaindb.backend import connect, query
from bigchaindb.web.views.base import make_error

logger = logging.getLogger(__name__)


class AssetListApi(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('text_search', type=str, required=True)
        args = parser.parse_args()

        text_query = args['text_search']
        if text_query:
            assets = query.text_search(connect(), text_query)
            return list(assets)
        else:
            return make_error(400, 'text_search cannot be empty')
