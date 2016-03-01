"""This module provides the blueprint for some basic API endpoints.

For more information please refer to the documentation in Apiary:
 - http://docs.bigchaindb.apiary.io/
"""

import flask
from flask import request, Blueprint

from bigchaindb import util
from bigchaindb import Bigchain


basic_views = Blueprint('basic_views', __name__)
b = Bigchain()


@basic_views.route('/transactions/<tx_id>')
def get_transaction(tx_id):
    """API endpoint to get details about a transaction.

    Args:
        tx_id (str): the id of the transaction.

    Return:
        A JSON string containing the data about the transaction.
    """

    tx = b.get_transaction(tx_id)
    return flask.jsonify(**tx)


@basic_views.route('/transactions/', methods=['POST'])
def create_transaction():
    """API endpoint to push transactions to the Federation.

    Return:
        A JSON string containing the data about the transaction.
    """

    val = {}

    # `force` will try to format the body of the POST request even if the `content-type` header is not
    # set to `application/json`
    tx = request.get_json(force=True)

    if tx['transaction']['operation'] == 'CREATE':
        tx = util.transform_create(tx)
        tx = util.sign_tx(tx, b.me_private)

    if not util.verify_signature(tx):
        val['error'] = 'Invalid transaction signature'

    val = b.write_transaction(tx)

    return flask.jsonify(**tx)

