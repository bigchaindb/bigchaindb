# Copyright © 2020 Interplanetary Database Association e.V.,
# BigchainDB and IPDB software contributors.
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

"""This module provides the blueprint for some basic API endpoints.

For more information please refer to the documentation: http://bigchaindb.com/http-api
"""
import json
from json import JSONEncoder
import logging
from bson import ObjectId
from flask_restful import reqparse, Resource
from flask import current_app, request, jsonify

from bigchaindb.backend.exceptions import OperationError
from bigchaindb.web.views.base import make_error

logger = logging.getLogger(__name__)


class ResultsJSONEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


class AssetListApi(Resource):
    def get(self):
        """API endpoint to perform a text search on the assets.

        Args:
            search (str): Text search string to query the text index
            limit (int, optional): Limit the number of returned documents.

        Return:
            A list of assets that match the query.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('search', type=str, required=True)
        parser.add_argument('limit', type=int)
        args = parser.parse_args()

        if not args['search']:
            return make_error(400, 'text_search cannot be empty')
        if not args['limit']:
            # if the limit is not specified do not pass None to `text_search`
            del args['limit']

        pool = current_app.config['bigchain_pool']

        with pool() as bigchain:
            assets = bigchain.text_search(**args)

        try:
            # This only works with MongoDB as the backend
            return list(assets)
        except OperationError as e:
            return make_error(
                400,
                '({}): {}'.format(type(e).__name__, e)
            )


class AssetQueryApi(Resource):
    def get(self):
        """API endpoint to perform a json query on the assets.

        Args:
            json_query (str): A MongoDB json search query.
            limit (int, optional): Limit the number of returned documents.

        Return:
            A list of assets that match the query.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('query', type=str)
        parser.add_argument('limit', type=int)
        args = parser.parse_args()

        if not args['limit']:
            # if the limit is not specified do not pass None to `text_search`
            del args['limit']

        if not args['query']:
            return make_error(
                400,
                'No query specified'
            )
        query = json.loads(args['query'])
        del args['query']
        print(f"QUERY:{query}")
        pool = current_app.config['bigchain_pool']
        with pool() as bigchain:
            assets = list(bigchain.query(json_query=query, **args))

        try:
            return json.dumps(assets, cls=ResultsJSONEncoder)
        except OperationError as e:
            return make_error(
                400,
                '({}): {}'.format(type(e).__name__, e)
            )


class AssetAggregateApi(Resource):
    def get(self):
        """API endpoint to perform a json query on the assets.

        Args:
            json_query (str): A MongoDB json search query.
            limit (int, optional): Limit the number of returned documents.

        Return:
            A list of assets that match the query.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('aggregation_functions', type=str)
        args = parser.parse_args()

        if not args['aggregation_functions']:
            return make_error(
                400,
                'No aggregation_functions specified'
            )
        aggregation_functions = json.loads(args['aggregation_functions'])
        if 'function_list' not in aggregation_functions.keys():
            return make_error(
                400,
                'Invalid json format'
            )
        function_list = aggregation_functions['function_list']
        del args['aggregation_functions']

        pool = current_app.config['bigchain_pool']
        with pool() as bigchain:
            results = list(bigchain.aggregate(
                aggregation_functions=function_list,
                **args))
        try:
            return json.dumps({"results": results}, cls=ResultsJSONEncoder)
        except OperationError as e:
            return make_error(
                400,
                '({}): {}'.format(type(e).__name__, e)
            )
