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
        return flask.jsonify({
            'api': {
                'v1': get_api_v1_info()
            },
            'docs': ''.join(docs_url),
            'software': 'BigchainDB',
            'version': version.__version__,
            'public_key': bigchaindb.config['keypair']['public'],
            'keyring': bigchaindb.config['keyring']
        })


class ApiV1Index(Resource):
    def get(self):
        return flask.jsonify(get_api_v1_info())


def get_api_v1_info():
    """
    Return a dict with all the information specific for the v1 of the
    api.
    """
    api_root = base_url() + 'api/v1/'
    websocket_root = base_ws_uri() + EVENTS_ENDPOINT
    docs_url = [
        'https://docs.bigchaindb.com/projects/server/en/v',
        version.__version__,
        '/http-client-server-api.html',
    ]

    return {
        'docs': ''.join(docs_url),
        'transactions': api_root + 'transactions/',
        'statuses': api_root + 'statuses/',
        'assets': api_root + 'assets/',
        'outputs': api_root + 'outputs/',
        'streams_v1': websocket_root
    }
