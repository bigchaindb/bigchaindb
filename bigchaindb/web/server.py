"""This module contains basic functions to instantiate the BigchainDB API. """

from flask import Flask

from bigchaindb import Bigchain
from bigchaindb.web import views


def create_app(debug=False):
    """Return an instance of the Flask application.

    Args:
        debug (bool): a flag to activate the debug mode for the app (default: False).
    """

    app = Flask(__name__)
    app.debug = debug
    app.config['bigchain'] = Bigchain()
    app.register_blueprint(views.basic_views, url_prefix='/api/v1')
    return app

