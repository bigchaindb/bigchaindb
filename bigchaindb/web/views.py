"""This module provides the blueprint for some basic API endpoints.

For more information please refer to the documentation in Apiary:
 - http://docs.bigchaindb.apiary.io/
"""

import flask
from flask import current_app, request, Blueprint

from bigchaindb import util, exceptions


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
    if not tx: flask.abort(404)
    return flask.jsonify(**tx)


@basic_views.route('/transactions/', methods=['POST'])
def create_transaction():
    """API endpoint to push transactions to the Federation.

    Return:
        A JSON string containing the data about the transaction.
    """
    bigchain = current_app.config['bigchain']

    val = {}

    # `force` will try to format the body of the POST request even if the
    # `content-type` header is not set to `application/json`
    tx = request.get_json(force=True)

    if tx['transaction']['operation'] == 'CREATE':
        tx = util.transform_create(tx)
        tx = bigchain.consensus.sign_transaction(
            tx, private_key=bigchain.me_private)

    if not bigchain.consensus.verify_signature(tx):
        val['error'] = 'Invalid transaction signature'

    val = bigchain.write_transaction(tx)

    return flask.jsonify(**tx)

@basic_views.route('/transactions/validate/', methods=['POST'])
def validate_transaction():
    """API endpoint to validate transactions without pushing them to the
    Federation. No federation node signature is required for `CREATE`
    transactions.

    Return:
        A JSON object with the `valid` field populated with a boolean value
        and the `error` field populated with an error message or an empty str
    """
    bigchain = current_app.config['bigchain']

    tx = request.get_json(force=True)

    if tx['transaction']['operation'] == 'CREATE':
        tx = util.transform_create(tx)

    try:
        bigchain.validate_transaction(tx)
    except exceptions.InvalidSignature as e:
        # We skipped signing CREATEs with the node's private key, so expect this
        if tx['transaction']['operation'] != 'CREATE':
            return flask.jsonify({'valid': False, 'error': repr(e)})
    except Exception as e:
        return flask.jsonify({'valid': False, 'error': repr(e)})

    return flask.jsonify({'valid': True, 'error': ''})
