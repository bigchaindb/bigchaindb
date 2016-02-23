import flask
from flask import Blueprint

from bigchaindb import Bigchain

basic_views = Blueprint('basic_views', __name__)
b = Bigchain()

@basic_views.route('/tx/<tx_id>')
def show(tx_id):
    tx = b.get_transaction(tx_id)
    return flask.jsonify(**tx)

