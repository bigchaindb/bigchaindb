import flask
from flask import current_app, request, Blueprint
from bigchaindb import crypto

import traceback

rpc_views = Blueprint('rpc_views', __name__)

@rpc_views.route('/bigchaindb', methods=['POST'])
def rpc_bigchaindb():
    try:
        rpc_request = request.get_json(force=True)
        method_name = rpc_request["method"]
        pool = current_app.config['bigchain_pool']
        with pool() as bigchain:
            method = getattr(bigchain, method_name)
            if not callable(method):
                return flask.jsonify(result=bigchain.__dict__[method_name])
            else:
                if "params" in rpc_request:
                    result = method(**rpc_request["params"])
                else:
                    result = method()
                return flask.jsonify(result=result)
    except:
        response = flask.jsonify(exception=traceback.format_exc())
        response.status_code = 500
        return response


@rpc_views.route('/crypto', methods=['POST'])
def rpc_crypto():
    try:
        rpc_request = request.get_json(force=True)
        method_name = rpc_request["method"]
        method = getattr(crypto, method_name)
        if not callable(method):
            return flask.jsonify(crypto=bigchain.__dict__[method_name])
        else:
            if "params" in rpc_request:
                result = method(**rpc_request["params"])
            else:
                result = method()
            return flask.jsonify(result=result)

    except:
        response = flask.jsonify(exception=traceback.format_exc())
        response.status_code = 500
        return response
