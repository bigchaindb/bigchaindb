""" API Index endpoint """

import flask
from flask_restful import Resource

import bigchaindb
from bigchaindb import version


class IndexApi(Resource):
    def get(self):
        return flask.jsonify({
            'software': 'BigchainDB',
            'version': version.__version__,
            'public_key': bigchaindb.config['keypair']['public'],
            'keyring': bigchaindb.config['keyring']
        })
