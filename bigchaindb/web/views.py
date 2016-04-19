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
    bigchain_pool = state.app.config.get('bigchain_pool')

    if bigchain_pool is None:
        raise Exception('This blueprint expects you to provide '
                        'a pool of Bigchain instances called `bigchain_pool`')


@basic_views.route('/transactions/<tx_id>')
def get_transaction(tx_id):
    """API endpoint to get details about a transaction.

    Args:
        tx_id (str): the id of the transaction.

    Return:
        A JSON string containing the data about the transaction.
    """

    pool = current_app.config['bigchain_pool']

    with pool() as bigchain:
        tx = bigchain.get_transaction(tx_id)

    return flask.jsonify(**tx)


@basic_views.route('/transactions/', methods=['POST'])
def create_transaction():
    """API endpoint to push transactions to the Federation.

    Return:
        A JSON string containing the data about the transaction.
    """
    pool = current_app.config['bigchain_pool']

    val = {}

    # `force` will try to format the body of the POST request even if the `content-type` header is not
    # set to `application/json`
    tx = request.get_json(force=True)

    with pool() as bigchain:
        if tx['transaction']['operation'] == 'CREATE':
            tx = util.transform_create(tx)
            tx = bigchain.consensus.sign_transaction(tx, private_key=bigchain.me_private)

        if not bigchain.consensus.verify_signature(tx):
            val['error'] = 'Invalid transaction signature'

        val = bigchain.write_transaction(tx)

    return flask.jsonify(**tx)

