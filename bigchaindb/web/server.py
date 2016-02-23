from flask import Flask

from bigchaindb.web import views


def create_app(debug=False):
    app = Flask(__name__)
    app.debug = debug
    app.register_blueprint(views.basic_views)
    return app


if __name__ == '__main__':
    create_app().run()

