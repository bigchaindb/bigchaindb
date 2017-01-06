""" API Index endpoint """

import flask
from flask_restful import Resource

import bigchaindb
from bigchaindb.web.views.base import base_url
from bigchaindb import version


class RootIndex(Resource):
    def get(self):
        return flask.jsonify({
            'software': 'BigchainDB',
            'version': version.__version__,
            'public_key': bigchaindb.config['keypair']['public'],
            'keyring': bigchaindb.config['keyring']
        })


class ApiV1Index(Resource):
    def get(self):
        api_root = base_url() + 'api/v1/'
        docs_url = ['https://docs.bigchaindb.com/projects/server/en/',
                    version.__short_version__,
                    '/drivers-clients/http-client-server-api.html',
                    ]

        return {
            "_links": {
                "docs": {"href": ''.join(docs_url)},
                "self": {"href": api_root},
                "statuses": {"href": api_root + "statuses/"},
                "transactions": {"href": api_root + "transactions/"},
            },
        }
