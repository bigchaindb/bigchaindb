""" API Index endpoint """

import flask
from flask_restful import Resource

import bigchaindb
from bigchaindb.web.views.base import base_url, base_ws_uri
from bigchaindb import version
from bigchaindb.web.websocket_server import EVENTS_ENDPOINT


class RootIndex(Resource):
    def get(self):
        docs_url = [
            'https://docs.bigchaindb.com/projects/server/en/v',
            version.__version__ + '/'
        ]
        api_v1_url = base_url() + 'api/v1/'
        return flask.jsonify({
            '_links': {
                'docs': ''.join(docs_url),
                'api_v1': api_v1_url,
            },
            'software': 'BigchainDB',
            'version': version.__version__,
            'public_key': bigchaindb.config['keypair']['public'],
            'keyring': bigchaindb.config['keyring']
        })


class ApiV1Index(Resource):
    def get(self):
        api_root = base_url() + 'api/v1/'
        websocket_root = base_ws_uri() + EVENTS_ENDPOINT
        docs_url = [
            'https://docs.bigchaindb.com/projects/server/en/v',
            version.__version__,
            '/http-client-server-api.html',
        ]
        return flask.jsonify({
            '_links': {
                'docs': ''.join(docs_url),
                'self': api_root,
                'statuses': api_root + 'statuses/',
                'transactions': api_root + 'transactions/',
                'streams_v1': websocket_root,
            },
        })
