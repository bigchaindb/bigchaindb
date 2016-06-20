"""This module provides the blueprint for some basic API endpoints.

For more information please refer to the documentation in Apiary:
 - http://docs.bigchaindb.apiary.io/
"""

import flask
from flask import abort, current_app, request, Blueprint

import bigchaindb
from bigchaindb import util, version


info_views = Blueprint('info_views', __name__)
basic_views = Blueprint('basic_views', __name__)


# Unfortunately I cannot find a reference to this decorator.
# This answer on SO is quite useful tho:
# - http://stackoverflow.com/a/13432373/597097
@basic_views.record
def record(state):
    """This function checks if the blueprint can be initialized
    with the provided state."""

    bigchain_pool = state.app.config.get('bigchain_pool')
    monitor = state.app.config.get('monitor')

    if bigchain_pool is None:
        raise Exception('This blueprint expects you to provide '
                        'a pool of Bigchain instances called `bigchain_pool`')

    if monitor is None:
        raise ValueError('This blueprint expects you to provide '
                         'a monitor instance to record system '
                         'performance.')

@info_views.route('/')
def home():
    return flask.jsonify({
        'software': 'BigchainDB',
        'version': version.__version__,
        'public_key': bigchaindb.config['keypair']['public'],
        'keyring': bigchaindb.config['keyring'],
        'api_endpoint': bigchaindb.config['api_endpoint']
    })


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

    if not tx:
        abort(404)

    return flask.jsonify(**tx)


@basic_views.route('/transactions/', methods=['POST'])
def create_transaction():
    """API endpoint to push transactions to the Federation.

    Return:
        A JSON string containing the data about the transaction.
    """
    pool = current_app.config['bigchain_pool']
    monitor = current_app.config['monitor']

    val = {}

    # `force` will try to format the body of the POST request even if the `content-type` header is not
    # set to `application/json`
    tx = request.get_json(force=True)

    with pool() as bigchain:
        if tx['transaction']['operation'] == 'CREATE':
            tx = util.transform_create(tx)
            tx = bigchain.consensus.sign_transaction(tx, private_key=bigchain.me_private)

        if not bigchain.consensus.validate_fulfillments(tx):
            val['error'] = 'Invalid transaction fulfillments'

        with monitor.timer('write_transaction', rate=bigchaindb.config['statsd']['rate']):
            val = bigchain.write_transaction(tx)

    return flask.jsonify(**tx)

