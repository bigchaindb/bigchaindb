"""
Common classes and methods for API handlers
"""

from flask import jsonify, request


def make_error(status_code, message=None):
    if status_code == 404 and message is None:
        message = 'Not found'

    response = jsonify({
        'status': status_code,
        'message': message
    })
    response.status_code = status_code
    return response


def base_url():
    return '%s://%s/' % (request.environ['wsgi.url_scheme'],
                         request.environ['HTTP_HOST'])
