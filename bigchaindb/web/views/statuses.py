"""This module provides the blueprint for the statuses API endpoints.

For more information please refer to the documentation on ReadTheDocs:
 - https://docs.bigchaindb.com/projects/server/en/latest/drivers-clients/
   http-client-server-api.html
"""
from flask import current_app
from flask_restful import Resource, reqparse

from bigchaindb.web.views.base import make_error


class StatusApi(Resource):
    def get(self):
        """API endpoint to get details about the status of a transaction or a block.

        Return:
            A ``dict`` in the format ``{'status': <status>}``, where
            ``<status>`` is one of "valid", "invalid", "undecided", "backlog".
        """
        parser = reqparse.RequestParser()
        parser.add_argument('tx_id', type=str)
        parser.add_argument('block_id', type=str)

        args = parser.parse_args(strict=True)

        if sum(arg is not None for arg in args.values()) != 1:
            return make_error(400, "Provide exactly one query parameter. Choices are: block_id, tx_id")

        pool = current_app.config['bigchain_pool']
        status, links = None, None

        with pool() as bigchain:
            if args['tx_id']:
                status = bigchain.get_status(args['tx_id'])
                links = {
                    "tx": "/transactions/{}".format(args['tx_id'])
                }

            elif args['block_id']:
                block = bigchain.get_block(block_id=args['block_id'])
                if not block:
                    return make_error(404)
                status = bigchain.block_election_status(block['id'], block['block']['voters'])
                # TODO: enable once blocks endpoint is available
                # links = {
                #     "block": "/blocks/{}".format(args['block_id'])
                # }

        if not status:
            return make_error(404)

        response = {
            'status': status
        }

        if links:
            response.update({
                "_links": links
            })

        return response
