"""This module provides the blueprint for some basic API endpoints.

For more information please refer to the documentation in Apiary:
 - http://docs.bigchaindb.apiary.io/
"""

import flask
from flask import current_app, request, Blueprint

from bigchaindb import util


basic_views = Blueprint('basic_views', __name__)


@basic_views.record
def get_bigchain(state):
    bigchain = state.app.config.get('bigchain')

    if bigchain is None:
        raise Exception('This blueprint expects you to provide '
                        'database access through `bigchain`')



@basic_views.route('/transactions/<tx_id>')
def get_transaction(tx_id):
    """API endpoint to get details about a transaction.

    Args:
        tx_id (str): the id of the transaction.

    Return:
        A JSON string containing the data about the transaction.
    """

    bigchain = current_app.config['bigchain']

    tx = bigchain.get_transaction(tx_id)
    return flask.jsonify(**tx)


@basic_views.route('/transactions/', methods=['POST'])
def create_transaction():
    """API endpoint to push transactions to the Federation.

    Return:
        A JSON string containing the data about the transaction.
    """
    bigchain = current_app.config['bigchain']

    val = {}

    # `force` will try to format the body of the POST request even if the `content-type` header is not
    # set to `application/json`
    tx = request.get_json(force=True)

    if tx['transaction']['operation'] == 'CREATE':
        tx = util.transform_create(tx)
        tx = util.sign_tx(tx, bigchain.me_private)

    if not util.verify_signature(tx):
        val['error'] = 'Invalid transaction signature'

    val = bigchain.write_transaction(tx)

    return flask.jsonify(**tx)

