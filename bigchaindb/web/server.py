"""This module contains basic functions to instantiate the BigchainDB API.

The application is implemented in Flask and runs using Gunicorn.
"""

import copy
import multiprocessing

from flask import Flask
from flask_cors import CORS
import gunicorn.app.base

from bigchaindb import utils
from bigchaindb import BigchainDB
from bigchaindb.web.routes import add_routes
from bigchaindb.web.strip_content_type_middleware import StripContentTypeMiddleware


# TODO: Figure out if we do we need all this boilerplate.
class StandaloneApplication(gunicorn.app.base.BaseApplication):
    """Run a **wsgi** app wrapping it in a Gunicorn Base Application.

    Adapted from:
     - http://docs.gunicorn.org/en/latest/custom.html
    """

    def __init__(self, app, *, options=None):
        """Initialize a new standalone application.

        Args:
            app: A wsgi Python application.
            options (dict): the configuration.

        """
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        # find a better way to pass this such that
        # the custom logger class can access it.
        custom_log_config = self.options.get('custom_log_config')
        self.cfg.env_orig['custom_log_config'] = custom_log_config

        config = dict((key, value) for key, value in self.options.items()
                      if key in self.cfg.settings and value is not None)

        config['default_proc_name'] = 'bigchaindb_gunicorn'
        for key, value in config.items():
            # not sure if we need the `key.lower` here, will just keep
            # keep it for now.
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


def create_app(*, debug=False, threads=1, bigchaindb_factory=None):
    """Return an instance of the Flask application.

    Args:
        debug (bool): a flag to activate the debug mode for the app
            (default: False).
        threads (int): number of threads to use
    Return:
        an instance of the Flask application.
    """

    if not bigchaindb_factory:
        bigchaindb_factory = BigchainDB

    app = Flask(__name__)
    app.wsgi_app = StripContentTypeMiddleware(app.wsgi_app)

    CORS(app)

    app.debug = debug

    app.config['bigchain_pool'] = utils.pool(bigchaindb_factory, size=threads)

    add_routes(app)

    return app


def create_server(settings, log_config=None, bigchaindb_factory=None):
    """Wrap and return an application ready to be run.

    Args:
        settings (dict): a dictionary containing the settings, more info
            here http://docs.gunicorn.org/en/latest/settings.html

    Return:
        an initialized instance of the application.
    """

    settings = copy.deepcopy(settings)

    if not settings.get('workers'):
        settings['workers'] = (multiprocessing.cpu_count() * 2) + 1

    if not settings.get('threads'):
        # Note: Threading is not recommended currently, as the frontend workload
        # is largely CPU bound and parallisation across Python threads makes it
        # slower.
        settings['threads'] = 1

    settings['custom_log_config'] = log_config
    app = create_app(debug=settings.get('debug', False),
                     threads=settings['threads'],
                     bigchaindb_factory=bigchaindb_factory)
    standalone = StandaloneApplication(app, options=settings)
    return standalone
