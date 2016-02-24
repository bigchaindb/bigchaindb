import flask
from flask import request, Blueprint

from bigchaindb import util
from bigchaindb import Bigchain

basic_views = Blueprint('basic_views', __name__)
b = Bigchain()


@basic_views.route('/tx/<tx_id>')
def get_transaction(tx_id):
    tx = b.get_transaction(tx_id)
    return flask.jsonify(**tx)


@basic_views.route('/tx/', methods=['POST'])
def create_transaction():
    val = {}
    tx = request.get_json(force=True)

    if tx['operation'] == 'CREATE':
        tx = util.transform_create(tx)
        tx = util.sign_tx(tx, b.me_private)

    if not util.verify_signature(tx):
        val['error'] = 'Invalid transaction signature'

    val = b.write_transaction(tx)

    return flask.jsonify(**tx)

