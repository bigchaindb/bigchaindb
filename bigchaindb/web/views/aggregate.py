# Tatau

"""This module provides the blueprint for some basic API endpoints.

For more information please refer to the documentation: http://bigchaindb.com/http-api
"""
import logging
import types
import json
from bson import json_util

from flask_restful import  Resource
from flask import request, current_app

from bigchaindb.backend.exceptions import OperationError
from bigchaindb.web.views.base import make_error
from bigchaindb.tatau_backend import query


logger = logging.getLogger(__name__)


class AggregateListApi(Resource):

    def post(self):
        """API endpoint to aggregate.

        Args:
            pipeline (str): Request of aggregate in body.

        Return:
            A list of aggregate the query.
        """
        table = request.args.get('table')
        if not table:
            table = 'transactions'
            # return make_error(400, 'table cannot be empty')
        try:
            pipeline = request.get_json(force=True)

        except Exception as e:
            return make_error(400, 'Json required')

        pool = current_app.config['bigchain_pool']

        with pool() as bigchain:
            def aggregate(obj, pipeline, table):
                return query.aggregate(obj.connection, pipeline, table)

            bigchain.aggregate = types.MethodType(aggregate, bigchain)
            data = bigchain.aggregate(pipeline, table)

        try:
            return json.loads(json_util.dumps(data))
        except OperationError as e:
            return make_error(
                400,
                '({}): {}'.format(type(e).__name__, e)
            )
